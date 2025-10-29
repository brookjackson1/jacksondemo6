import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

print("Connected to database successfully!")

# Sample movies to add (just titles - use "Fetch Data" to populate details from OMDB)
sample_movies = [
    'The Shawshank Redemption',
    'The Godfather',
    'The Dark Knight',
    'Pulp Fiction',
    'Inception',
    'Star Wars',
    'Dances with Wolves',
    'Star Trek',
    'The Godfather Part II',
]

try:
    with connection.cursor() as cursor:
        # Check if movies already exist
        cursor.execute("SELECT COUNT(*) as count FROM movies")
        result = cursor.fetchone()

        if result['count'] > 0:
            print(f"\n[INFO] Database already has {result['count']} movie(s).")
            response = input("Do you want to add sample movies anyway? (y/n): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                connection.close()
                exit()

        # Insert sample movies (title only)
        insert_query = """
        INSERT INTO movies (title, director, year, plot, poster, actors, genre)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        added_count = 0
        for title in sample_movies:
            try:
                cursor.execute(insert_query, (title, None, None, None, None, None, None))
                print(f"[SUCCESS] Added '{title}'")
                added_count += 1
            except pymysql.err.IntegrityError as e:
                print(f"[ERROR] Failed to add '{title}': {e}")

    connection.commit()
    print(f"\n[SUCCESS] Added {added_count} movies!")
    print("\nNext steps:")
    print("1. Get your OMDB API key at: http://www.omdbapi.com/apikey.aspx")
    print("2. Add OMDB_API_KEY to your .env file")
    print("3. Visit /movies and click 'Fetch Data' for each movie to populate details!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    connection.rollback()
finally:
    connection.close()
    print("\nDatabase connection closed.")
