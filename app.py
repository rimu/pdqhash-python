from quart import Quart, request, jsonify, json
import pdqhash
from PIL import Image
import io
import os
import httpx
import numpy as np
from quart_rate_limiter import RateLimiter, rate_limit
from datetime import timedelta
from quart_redis import RedisHandler, get_redis


app = Quart(__name__)
rate_limiter = RateLimiter(app)
app.config["REDIS_URI"] = os.environ.get('REDIS_URI') or "redis://localhost"
redis_handler = RedisHandler(app)



@app.route('/pdq-hash', methods=['GET'])
@rate_limit(10, timedelta(seconds=1))
@rate_limit(60, timedelta(minutes=1))
async def pdq_hash_route():
    image_url = request.args.get("image_url")
    if not image_url:
        return jsonify({"error": "Missing 'image_url' query parameter"}), 400

    redis = get_redis()
    val = await redis.get(image_url)
    
    if val:
        return jsonify(json.loads(val))


    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, follow_redirects=True)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Failed to fetch or decode image: {str(e)}"}), 400

    try:
        np_img = np.array(img)
        hash_bits, quality = pdqhash.compute(np_img)

        # Convert the bit array (bools or 0/1) to a string of '0' and '1'
        hash_binary_str = ''.join(str(int(b)) for b in hash_bits)

        return_value = {
            "pdq_hash_binary": hash_binary_str,
            "quality": quality
        }

        await redis.set(image_url, json.dumps(return_value), ex=3600)

        return jsonify(return_value)
    except Exception as e:
        return jsonify({"error": f"Hashing failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)


# The `quality` score (0–100) indicates how well the image content supports a reliable perceptual hash.
# Higher scores mean better contrast, edges, and texture in the image.

# | Quality Score | Interpretation                               |
# |---------------|----------------------------------------------|
# | 90–100        | Excellent — strong, high-confidence hash     |
# | 70–89         | Good — usable hash                           |
# | 50–69         | Marginal — hash may be weak or ambiguous     |
# | Below 50      | Poor — not recommended for reliable matching |
