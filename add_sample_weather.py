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

# Sample weather cities to add
sample_weather = [
    ('Atlanta', 'Georgia', 48.0),
    ('Milledgeville', 'Georgia', 68.0),
    ('New York', 'New York', 55.0),
    ('Los Angeles', 'California', 76.0),
    ('Chicago', 'Illinois', 46.0),
    ('Miami', 'Florida', 82.0),
    ('Seattle', 'Washington', 59.0),
    ('Austin', 'Texas', 78.0),
    ('Boston', 'Massachusetts', 66.0),
    ('Denver', 'Colorado', 69.0),
    ('Gray', 'Georgia', 45.0),
    ('Macon', 'Georgia', 82.0),
]

try:
    with connection.cursor() as cursor:
        # Check if weather records already exist
        cursor.execute("SELECT COUNT(*) as count FROM weather")
        result = cursor.fetchone()

        if result['count'] > 0:
            print(f"\n[INFO] Database already has {result['count']} weather record(s).")
            response = input("Do you want to add sample cities anyway? (y/n): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                connection.close()
                exit()

        # Insert sample weather cities
        insert_query = """
        INSERT INTO weather (city, state, temperature)
        VALUES (%s, %s, %s)
        """

        added_count = 0
        for city, state, temperature in sample_weather:
            try:
                cursor.execute(insert_query, (city, state, temperature))
                print(f"[SUCCESS] Added {city}, {state} - {temperature}°F")
                added_count += 1
            except pymysql.err.IntegrityError as e:
                print(f"[ERROR] Failed to add {city}: {e}")

    connection.commit()
    print(f"\n[SUCCESS] Added {added_count} weather cities!")
    print("\nYou can now update temperatures using the 'Update Weather' button on the web interface.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    connection.rollback()
finally:
    connection.close()
    print("\nDatabase connection closed.")
