# piefed-pdqhash

PDQ Hashes are used to detect similar images. 256 ones and zeros are generated which are a fairly unique fingerprint for that image. By comparing the hash of images and checking
how many of the ones and zeros are different we can detect if an image is a slightly modified version of another image. This is very helpful for checking if user-submitted
images are on a block-list of undesirable images.

This project puts a REST API in-front of https://github.com/faustomorales/pdqhash-python.

## API

By doing a GET request for https://yourdomain.tld/pdq-hash?image_url=url_to_image_to_hash you will receive JSON like this:

```
{
    "pdq_hash_binary": "100100100011...",
    "quality": 100
}
```

The `quality` score (0–100) indicates how well the image content supports a reliable perceptual hash.

Higher scores mean better contrast, edges, and texture in the image.

 | Quality Score | Interpretation                               |
 |---------------|----------------------------------------------|
 | 90–100        | Excellent — strong, high-confidence hash     |
 | 70–89         | Good — usable hash                           |
 | 50–69         | Marginal — hash may be weak or ambiguous     |
 | Below 50      | Poor — not recommended for reliable matching |





## Example code

If you store your block-list in a PostgreSQL database with the hash in a field of type 'bit' then Python + SQL like this will give you all posts with blocked images:


```
def posts_with_blocked_images() -> List[int]:
    sql = """
    SELECT DISTINCT post.id
    FROM post
    JOIN file ON post.image_id = file.id
    JOIN blocked_image ON (
        length(replace((file.hash # blocked_image.hash)::text, '0', ''))
    ) < 15
    WHERE post.deleted = false AND file.hash is not null
    """

    return list(db.session.execute(text(sql)).scalars())

```

In this example 15 is the maximum number of bits that can be different for images to be considered so different that they are not the same image. Experiment to find a good value for your situation.

To check if a particular hash is in your block list, try something like this:

```
BINARY_RE = re.compile(r'^[01]+$')  # used in hash_matches_blocked_image()

def hash_matches_blocked_image(hash: str) -> bool:
    # calculate hamming distance between the provided hash and the hashes of all the blocked images.
    # the hamming distance is a value between 0 and 256 indicating how many bits are different.
    # 15 is the number of different bits we will accept. Anything less than that and we consider the images to be the same.

    # only accept a string with 0 and 1 in it. This makes it safe to use sql injection-prone code below, which greatly simplifies the conversion of binary strings
    if not BINARY_RE.match(hash):
        current_app.logger.warning(f"Invalid binary hash: {hash}")
        return False

    sql = f"""SELECT id FROM blocked_image WHERE length(replace((hash # B'{hash}')::text, '0', '')) < 15;"""
    blocked_images = db.session.execute(text(sql)).scalars().first()
    return blocked_images is not None
```

This SQL is a bit weird looking so you might prefer to calculate the hamming distance in python instead. This will be fine if the length of your block list is small.




## Installation

See INSTALL.md for installation instructions.
