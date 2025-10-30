from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Groq API...")
print("=" * 60)

# Check if API key exists
api_key = os.getenv('GROQ_API_KEY')
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")

if not api_key:
    print("\n[ERROR] GROQ_API_KEY not set in .env file")
    exit()

try:
    # Initialize Groq client
    print("\n[STEP 1] Initializing Groq client...")
    client = Groq(api_key=api_key)
    print("[SUCCESS] Client initialized")

    # Test with a simple question
    print("\n[STEP 2] Sending test question: 'What is 2+2?'")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "What is 2+2?",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    response = chat_completion.choices[0].message.content
    print(f"\n[SUCCESS] Got response:")
    print(f"Response: {response}")

    print("\n" + "=" * 60)
    print("[RESULT] Groq API is working correctly!")

except Exception as e:
    print(f"\n[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
