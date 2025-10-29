import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM weather WHERE city = 'Atlanta'")
    result = cursor.fetchone()

    if result:
        print(f"City: {result['city']}, {result['state']}")
        print(f"Temperature: {result['temperature']}°F")
        print(f"Last Updated: {result['updated_at']}")
    else:
        print("Atlanta not found in database")

connection.close()
