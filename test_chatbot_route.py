from app import app
from app.blueprints.chat import get_groq_response

print("Testing chatbot route directly...")
print("=" * 60)

# Test 1: Test the get_groq_response function
print("\n[TEST 1] Testing get_groq_response function...")
response = get_groq_response("What is 2+2?")

if response:
    print(f"[SUCCESS] Got response: {response}")
else:
    print("[ERROR] No response returned")

# Test 2: Test the Flask route
print("\n[TEST 2] Testing Flask route...")
with app.test_client() as client:
    # Test GET request
    print("  Testing GET /chatbot...")
    rv = client.get('/chatbot')
    print(f"  Status: {rv.status_code}")

    # Test POST request
    print("\n  Testing POST /chatbot/ask...")
    rv = client.post('/chatbot/ask', data={'question': 'What is 2+2?'})
    print(f"  Status: {rv.status_code}")

    if rv.status_code == 200:
        if b'Response:' in rv.data:
            print("  [SUCCESS] Response found in HTML")
            # Extract just the response text
            data_str = rv.data.decode('utf-8')
            if 'AI Response:' in data_str:
                start = data_str.find('AI Response:')
                snippet = data_str[start:start+200]
                print(f"  Snippet: {snippet[:100]}...")
        else:
            print("  [ERROR] No response in HTML")
            print(f"  HTML length: {len(rv.data)} bytes")

print("\n" + "=" * 60)
print("[COMPLETE]")
