from app import app
from app.db_connect import get_db
import os

# Test the fetch_data route manually
with app.app_context():
    print("Testing /movies/fetch/7 route...")
    print("=" * 60)

    # Simulate what the route does
    movie_id = 7

    connection = get_db()

    if connection is None:
        print("[ERROR] Database connection failed")
        exit()

    print("[SUCCESS] Database connected")

    try:
        # Get the movie title from database
        query = "SELECT title FROM movies WHERE movie_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

        if not movie:
            print("[ERROR] Movie not found in database")
            exit()

        title = movie['title']
        print(f"[SUCCESS] Found movie: {title}")

        # Check API key
        api_key = os.getenv('OMDB_API_KEY')
        print(f"[INFO] API Key: {api_key}")

        if not api_key:
            print("[ERROR] OMDB_API_KEY not set!")
            exit()

        # Try to fetch data
        from app.blueprints.movies import fetch_omdb_data
        print(f"\n[INFO] Calling fetch_omdb_data('{title}')...")

        movie_data = fetch_omdb_data(title)

        if movie_data is None:
            print("[ERROR] fetch_omdb_data returned None")
            exit()

        print(f"[SUCCESS] Data fetched!")
        print(f"Director: {movie_data.get('director')}")
        print(f"Year: {movie_data.get('year')}")
        print(f"Genre: {movie_data.get('genre')}")

        # Try to update database
        print(f"\n[INFO] Updating database...")
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

        print("\n[RESULT] The route should work correctly!")

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
