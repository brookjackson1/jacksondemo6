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

# Sample tickers to add
sample_tickers = [
    ('VTSAX', 'Vanguard Total Stock Market Index Fund', 100.00),
    ('AAPL', 'Apple Inc.', 175.00),
    ('GOOGL', 'Alphabet Inc.', 140.00),
    ('MSFT', 'Microsoft Corporation', 380.00),
    ('AMZN', 'Amazon.com Inc.', 145.00),
    ('TSLA', 'Tesla Inc.', 240.00),
    ('META', 'Meta Platforms Inc.', 350.00),
    ('NVDA', 'NVIDIA Corporation', 500.00),
    ('JPM', 'JPMorgan Chase & Co.', 155.00),
    ('V', 'Visa Inc.', 250.00),
    ('WMT', 'Walmart Inc.', 160.00),
]

try:
    with connection.cursor() as cursor:
        # Check if tickers already exist
        cursor.execute("SELECT COUNT(*) as count FROM tickers")
        result = cursor.fetchone()

        if result['count'] > 0:
            print(f"\n[INFO] Database already has {result['count']} ticker(s).")
            response = input("Do you want to add sample tickers anyway? (y/n): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                connection.close()
                exit()

        # Insert sample tickers
        insert_query = """
        INSERT INTO tickers (symbol, name, price)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name=VALUES(name), price=VALUES(price)
        """

        added_count = 0
        for symbol, name, price in sample_tickers:
            try:
                cursor.execute(insert_query, (symbol, name, price))
                print(f"[SUCCESS] Added {symbol} - {name}")
                added_count += 1
            except pymysql.err.IntegrityError as e:
                if "Duplicate entry" in str(e):
                    print(f"[INFO] {symbol} already exists, updated instead")
                else:
                    print(f"[ERROR] Failed to add {symbol}: {e}")

    connection.commit()
    print(f"\n[SUCCESS] Added/Updated {added_count} tickers!")
    print("\nYou can now update prices using the 'Update Price' button on the web interface.")

except Exception as e:
    print(f"\n[ERROR] {e}")
    connection.rollback()
finally:
    connection.close()
    print("\nDatabase connection closed.")
