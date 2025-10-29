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

# SQL to create movies table
movies_table_sql = """
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    year INT,
    plot TEXT,
    poster TEXT,
    actors TEXT,
    genre VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

index_title_sql = """
CREATE INDEX idx_movies_title ON movies (title)
"""

index_year_sql = """
CREATE INDEX idx_movies_year ON movies (year)
"""

try:
    with connection.cursor() as cursor:
        print("\nCreating movies table...")
        cursor.execute(movies_table_sql)
        print("[SUCCESS] Movies table created!")

        print("\nCreating index on title column...")
        try:
            cursor.execute(index_title_sql)
            print("[SUCCESS] Title index created!")
        except pymysql.err.OperationalError as e:
            if "Duplicate key name" in str(e):
                print("[INFO] Title index already exists, skipping...")
            else:
                raise

        print("\nCreating index on year column...")
        try:
            cursor.execute(index_year_sql)
            print("[SUCCESS] Year index created!")
        except pymysql.err.OperationalError as e:
            if "Duplicate key name" in str(e):
                print("[INFO] Year index already exists, skipping...")
            else:
                raise

    connection.commit()
    print("\n[SUCCESS] All schema updates completed successfully!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    connection.rollback()
finally:
    connection.close()
    print("\nDatabase connection closed.")
