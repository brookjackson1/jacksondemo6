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

# SQL to create weather table
weather_table_sql = """
CREATE TABLE IF NOT EXISTS weather (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    temperature DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

index_sql = """
CREATE INDEX idx_weather_city ON weather (city)
"""

try:
    with connection.cursor() as cursor:
        print("\nCreating weather table...")
        cursor.execute(weather_table_sql)
        print("[SUCCESS] Weather table created!")

        print("\nCreating index on city column...")
        try:
            cursor.execute(index_sql)
            print("[SUCCESS] Index created!")
        except pymysql.err.OperationalError as e:
            if "Duplicate key name" in str(e):
                print("[INFO] Index already exists, skipping...")
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
