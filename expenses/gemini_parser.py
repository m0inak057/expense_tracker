"""
Gemini AI-based expense parser using Google's free Gemini API.
This provides superior natural language parsing without API costs.
"""
import os
import json
import google.generativeai as genai
from datetime import datetime

def parse_expense_gemini(text):
    """
    Parse natural language expense description using Google Gemini AI.
    
    Args:
        text (str): Natural language expense description
        
    Returns:
        dict: Parsed expense data with amount, category, date, description
        
    Raises:
        Exception: If parsing fails or API error occurs
    """
    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash model (free tier, faster)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create structured prompt for expense parsing
        prompt = f"""
You are an expense parsing assistant. Parse the following expense description and return ONLY a JSON object (no markdown, no extra text).

Input: "{text}"

Return JSON with these exact fields:
{{
    "amount": <number in rupees>,
    "category": "<Food|Transport|Shopping|Entertainment|Bills|Healthcare|Other>",
    "date": "<YYYY-MM-DD format, use today's date if not mentioned>",
    "description": "<brief summary of expense>"
}}

Rules:
- Extract amount in rupees (₹). Convert if currency mentioned.
- Choose most appropriate category from the 7 options (Food, Transport, Shopping, Entertainment, Bills, Healthcare, Other)
- If category is clearly Transport/Auto/Taxi/Car, use "Transport" category
- If category is clearly Car-related (fuel, maintenance, parking), use "Transport" category  
- Use today's date ({datetime.now().strftime('%Y-%m-%d')}) if date not specified
- For description: Extract the actual PURPOSE/ITEM from the text, NOT just generic words
- Description should capture WHAT was purchased or service used (e.g., "Car maintenance", "Auto fare", "Groceries", "Dinner at restaurant")
- Keep description concise but specific (max 50 chars)
- Return ONLY valid JSON, no explanation

Examples:
Input: "Spent 500 rupees on car"
Output: {{"amount": 500, "category": "Transport", "date": "{datetime.now().strftime('%Y-%m-%d')}", "description": "Car maintenance"}}

Input: "Auto fare to office 50 rupees"
Output: {{"amount": 50, "category": "Transport", "date": "{datetime.now().strftime('%Y-%m-%d')}", "description": "Auto fare to office"}}

Input: "Spent 500 on groceries today"
Output: {{"amount": 500, "category": "Food", "date": "{datetime.now().strftime('%Y-%m-%d')}", "description": "Groceries"}}

Input: "Paid ₹1200 for dinner last night"
Output: {{"amount": 1200, "category": "Food", "date": "{(datetime.now()).strftime('%Y-%m-%d')}", "description": "Dinner"}}

Now parse the input above.
"""
        
        # Generate response
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini API")
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        print(f"DEBUG - Gemini raw response: {response_text}")
        
        # Parse JSON
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"DEBUG - JSON parsing failed: {str(e)}")
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
        
        # Validate required fields
        required_fields = ['amount', 'category', 'date', 'description']
        missing_fields = [field for field in required_fields if field not in parsed_data]
        
        if missing_fields:
            raise Exception(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate amount is numeric
        try:
            parsed_data['amount'] = float(parsed_data['amount'])
        except (ValueError, TypeError):
            raise Exception(f"Invalid amount value: {parsed_data.get('amount')}")
        
        # Validate category
        valid_categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Healthcare', 'Other']
        if parsed_data['category'] not in valid_categories:
            print(f"DEBUG - Invalid category '{parsed_data['category']}', defaulting to 'Other'")
            parsed_data['category'] = 'Other'
        
        # Validate date format
        try:
            datetime.strptime(parsed_data['date'], '%Y-%m-%d')
        except ValueError:
            print(f"DEBUG - Invalid date format '{parsed_data['date']}', using today")
            parsed_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"DEBUG - Successfully parsed expense: {parsed_data}")
        return parsed_data
        
    except Exception as e:
        print(f"ERROR in Gemini parser: {str(e)}")
        raise Exception(f"Gemini parsing failed: {str(e)}")
