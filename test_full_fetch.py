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

print("Testing complete fetch and update process...")
print("=" * 60)

movie_id = 7  # Dances with Wolves

try:
    # Step 1: Get the movie title from database
    query = "SELECT title FROM movies WHERE movie_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (movie_id,))
        movie = cursor.fetchone()

    if not movie:
        print("[ERROR] Movie not found")
        exit()

    title = movie['title']
    print(f"\n[STEP 1] Found movie: {title}")

    # Step 2: Fetch data from OMDB API
    print(f"\n[STEP 2] Fetching data from OMDB...")
    movie_data = fetch_omdb_data(title)

    if movie_data is None:
        print("[ERROR] Could not fetch data from OMDB")
        exit()

    print(f"[SUCCESS] Data fetched!")

    # Step 3: Update database with fetched data
    print(f"\n[STEP 3] Updating database...")
    update_query = """
    UPDATE movies
    SET director = %s, year = %s, plot = %s, poster = %s, actors = %s, genre = %s
    WHERE movie_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(update_query, (
            movie_data.get('director'),
            movie_data.get('year'),
            movie_data.get('plot'),
            movie_data.get('poster'),
            movie_data.get('actors'),
            movie_data.get('genre'),
            movie_id
        ))
    connection.commit()
    print("[SUCCESS] Database updated!")

    # Step 4: Verify the update
    print(f"\n[STEP 4] Verifying update...")
    verify_query = "SELECT * FROM movies WHERE movie_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(verify_query, (movie_id,))
        updated_movie = cursor.fetchone()

    print(f"\nVerified movie data:")
    print(f"Title: {updated_movie['title']}")
    print(f"Director: {updated_movie['director']}")
    print(f"Year: {updated_movie['year']}")
    print(f"Genre: {updated_movie['genre']}")
    print(f"Actors: {updated_movie['actors']}")
    print(f"Plot: {updated_movie['plot'][:100]}...")

    print("\n[SUCCESS] Complete fetch and update process working!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    connection.close()
