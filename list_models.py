from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

print("Fetching available Groq models...")
print("=" * 60)

try:
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    models = client.models.list()

    print("\nAvailable Models:")
    for model in models.data:
        print(f"  - {model.id}")

except Exception as e:
    print(f"Error: {e}")
