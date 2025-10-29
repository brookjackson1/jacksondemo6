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

print("Verifying tickers table structure...\n")

try:
    with connection.cursor() as cursor:
        # Show table structure
        cursor.execute("DESCRIBE tickers")
        columns = cursor.fetchall()

        print("Tickers Table Structure:")
        print("-" * 80)
        for col in columns:
            print(f"Column: {col['Field']:15} Type: {col['Type']:20} Null: {col['Null']:5} Key: {col['Key']:5}")

        # Show indexes
        cursor.execute("SHOW INDEX FROM tickers")
        indexes = cursor.fetchall()

        print("\n\nTable Indexes:")
        print("-" * 80)
        for idx in indexes:
            print(f"Index: {idx['Key_name']:20} Column: {idx['Column_name']:15} Unique: {idx['Non_unique'] == 0}")

    print("\n[SUCCESS] Tickers table is ready to use!")

except Exception as e:
    print(f"\n[ERROR] {e}")
finally:
    connection.close()
