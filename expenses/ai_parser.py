import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Determine which AI parser to use
USE_MOCK_PARSER = os.getenv("USE_MOCK_PARSER", "false").lower() == "true"
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"

def parse_expense(text):
    """Parse natural language expense text into structured data using AI"""
    
    # Priority 1: Use mock parser if explicitly enabled
    if USE_MOCK_PARSER:
        from .mock_parser import parse_expense_mock
        print("Using mock parser (free regex-based)")
        return parse_expense_mock(text)
    
    # Priority 2: Use Gemini if enabled (free and superior)
    if USE_GEMINI:
        try:
            from .gemini_parser import parse_expense_gemini
            print("Using Google Gemini AI parser (free)")
            return parse_expense_gemini(text)
        except Exception as e:
            print(f"Gemini parser failed: {str(e)}, falling back to mock parser")
            from .mock_parser import parse_expense_mock
            return parse_expense_mock(text)
    
    # Priority 3: Use OpenAI (requires paid API)
    
    # Get today's date as default
    today = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
Extract expense information from the text and return ONLY a valid JSON object (no markdown, no code blocks).

Required JSON format:
{{
    "amount": <number>,
    "category": "<string>",
    "date": "<YYYY-MM-DD>",
    "description": "<string>"
}}

Rules:
- amount: Extract the numeric value only (e.g., 50.00)
- category: Classify as Food, Transport, Shopping, Entertainment, Bills, Health, or Other
- date: If no date mentioned, use today's date: {today}
- description: Brief summary of the expense

TEXT: "{text}"

Return only the JSON object, nothing else.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expense parser. Return ONLY valid JSON. No explanations, no markdown formatting, just the JSON object."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=150
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Parse JSON
        parsed_data = json.loads(content)
        
        # Validate required fields
        required_fields = ['amount', 'category', 'date', 'description']
        for field in required_fields:
            if field not in parsed_data:
                print(f"Missing required field: {field}")
                return None
        
        # Ensure amount is a number
        parsed_data['amount'] = float(parsed_data['amount'])
        
        # Validate date format
        try:
            datetime.strptime(parsed_data['date'], "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {parsed_data['date']}, using today's date")
            parsed_data['date'] = today
        
        print(f"Successfully parsed expense: {parsed_data}")
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {content if 'content' in locals() else 'No content'}")
        return None
    except Exception as e:
        print(f"AI Parsing error: {type(e).__name__}: {e}")
        
        # Fallback to mock parser on API errors
        if "RateLimitError" in str(type(e).__name__) or "insufficient_quota" in str(e):
            print("OpenAI quota exceeded! Falling back to mock parser...")
            from .mock_parser import parse_expense_mock
            return parse_expense_mock(text)
        
        return None
