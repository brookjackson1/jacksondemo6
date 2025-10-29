import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OMDB_API_KEY')
print(f"Testing OMDB API with key: {api_key}")
print("=" * 60)

# Test with "The Shawshank Redemption"
title = "The Shawshank Redemption"
url = "http://www.omdbapi.com/"
params = {
    'apikey': api_key,
    't': title,
    'type': 'movie',
    'plot': 'full'
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get('Response') == 'True':
        print(f"\n[SUCCESS] Movie found:")
        print(f"Title: {data.get('Title')}")
        print(f"Director: {data.get('Director')}")
        print(f"Year: {data.get('Year')}")
        print(f"Genre: {data.get('Genre')}")
        print(f"Actors: {data.get('Actors')}")
        print(f"Plot: {data.get('Plot')[:100]}...")
        print(f"Poster: {data.get('Poster')}")
        print("\n[SUCCESS] Your OMDB API key is working perfectly!")
    else:
        print(f"\n[ERROR] {data.get('Error')}")

except Exception as e:
    print(f"\n[ERROR] Request failed: {e}")
