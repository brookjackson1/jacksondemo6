import pymysql
import os
from dotenv import load_dotenv
from app.blueprints.movies import fetch_omdb_data

load_dotenv()

# Connect to database
connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

print("Testing movie data fetch...")
print("=" * 60)

# Get a movie from the database
with connection.cursor() as cursor:
    cursor.execute("SELECT movie_id, title FROM movies LIMIT 1")
    movie = cursor.fetchone()

if movie:
    print(f"\nMovie ID: {movie['movie_id']}")
    print(f"Title: {movie['title']}")

    # Test fetching data from OMDB
    print(f"\nFetching data from OMDB for '{movie['title']}'...")
    movie_data = fetch_omdb_data(movie['title'])

    if movie_data:
        print("\n[SUCCESS] Data fetched:")
        print(f"Director: {movie_data.get('director')}")
        print(f"Year: {movie_data.get('year')}")
        print(f"Genre: {movie_data.get('genre')}")
        print(f"Actors: {movie_data.get('actors')}")
        print(f"Plot: {movie_data.get('plot')[:100]}...")
        print(f"Poster: {movie_data.get('poster')}")
    else:
        print("\n[ERROR] Could not fetch data from OMDB")
else:
    print("\n[ERROR] No movies in database")

connection.close()
