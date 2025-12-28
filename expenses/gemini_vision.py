"""
Gemini Vision AI for receipt scanning - instant, no downloads needed!
"""
import os
import json
import base64
import google.generativeai as genai
from datetime import datetime

def scan_receipt_with_gemini(image_data_url):
    """
    Scan receipt using Gemini Vision AI
    
    Args:
        image_data_url (str): Base64 data URL of the receipt image
        
    Returns:
        dict: Extracted receipt data with amount, category, date, description
    """
    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-flash-latest (proper model name for vision)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("Scanning receipt with Gemini 1.5 Flash...")
        
        # Extract base64 image data
        if ',' in image_data_url:
            image_data = image_data_url.split(',')[1]
        else:
            image_data = image_data_url
        
        # Decode base64 image to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Create prompt for receipt scanning
        prompt = f"""Analyze this receipt image and extract information.
Return ONLY a valid JSON object with these exact fields:

{{
    "amount": <total amount as number>,
    "category": "<Food|Transport|Shopping|Entertainment|Bills|Healthcare|Other>",
    "date": "<YYYY-MM-DD>",
    "description": "<merchant name or items>"
}}

Today is {datetime.now().strftime('%Y-%m-%d')}. Extract the total amount, merchant name, and date from the receipt.
If date is unclear, use today. Categorize based on merchant/items. Return valid JSON only."""
        
        # CORRECT FORMAT: Pass image as dict with mime_type and data (bytes)
        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
        ])
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini Vision API")
        
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
        
        print(f"DEBUG - Gemini Vision response: {response_text}")
        
        # Parse JSON
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"DEBUG - JSON parsing failed: {str(e)}")
            raise Exception(f"Failed to parse Gemini Vision response as JSON: {str(e)}")
        
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
        
        print(f"DEBUG - Successfully scanned receipt: {parsed_data}")
        return parsed_data
        
    except Exception as e:
        print(f"ERROR in Gemini Vision scanner: {str(e)}")
        raise Exception(f"Receipt scanning failed: {str(e)}")
