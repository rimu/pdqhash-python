import httpx
import asyncio

# Function to compute Hamming distance
def hamming_distance(hash1, hash2):
    if len(hash1) != len(hash2):
        raise ValueError("Hashes must be of the same length")
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

# Store hashes in a simple list (could be a database in a real application)
stored_hashes = []

async def get_pdq_hash(image_url):
    api_url = 'http://localhost:5000/pdq-hash'

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params={'image_url': image_url})
        
        if response.status_code == 200:
            data = response.json()

            pdq_hash_binary = data.get('pdq_hash_binary')
            quality = data.get('quality')

            print(f"New Image PDQ Hash (binary): {pdq_hash_binary}")
            print(f"Quality: {quality}")

            for stored_hash in stored_hashes:
                distance = hamming_distance(pdq_hash_binary, stored_hash)
                print(f"Hamming distance with stored hash: {distance}")

            stored_hashes.append(pdq_hash_binary)
        else:
            print(f"Error: {response.status_code} - {response.text}")

# Example usage
async def main():
    image_url = "https://example.com/path/to/image.jpg"
    await get_pdq_hash(image_url)

if __name__ == "__main__":
    asyncio.run(main())

