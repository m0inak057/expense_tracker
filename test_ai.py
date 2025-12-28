import os
from dotenv import load_dotenv
load_dotenv()

# Test 1: Check if API key exists
print("=" * 50)
print("TEST 1: Checking OpenAI API Key")
print("=" * 50)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✓ API Key found: {api_key[:20]}...")
else:
    print("✗ API Key not found!")
    exit(1)

# Test 2: Test OpenAI connection
print("\n" + "=" * 50)
print("TEST 2: Testing OpenAI Connection")
print("=" * 50)
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    print("✓ OpenAI client created successfully")
    
    # Test 3: Simple API call
    print("\n" + "=" * 50)
    print("TEST 3: Testing Simple API Call")
    print("=" * 50)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'Hello'"}
        ],
        max_tokens=10
    )
    print(f"✓ API call successful!")
    print(f"Response: {response.choices[0].message.content}")
    
    # Test 4: Test expense parsing
    print("\n" + "=" * 50)
    print("TEST 4: Testing Expense Parsing")
    print("=" * 50)
    from expenses.ai_parser import parse_expense
    
    test_text = "Spent $50 on groceries today"
    print(f"Input: {test_text}")
    result = parse_expense(test_text)
    
    if result:
        print("✓ Parsing successful!")
        print(f"Result: {result}")
    else:
        print("✗ Parsing failed!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
