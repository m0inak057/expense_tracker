import re
from datetime import datetime

def parse_expense_mock(text):
    """
    Mock expense parser that uses regex instead of AI
    Use this when OpenAI quota is exceeded
    """
    
    print(f"Mock parser processing: {text}")
    
    # Extract amount (supports ₹50, $50, 50 rupees, 50 dollars, etc.)
    amount_patterns = [
        r'₹(\d+\.?\d*)',            # ₹50 or ₹50.00
        r'\$(\d+\.?\d*)',           # $50 or $50.00
        r'(?:rs\.?|rupees?)\s*(\d+\.?\d*)',  # rs 50 or rupees 50
        r'(\d+\.?\d*)\s*(?:rs\.?|rupees?)',  # 50 rs or 50 rupees
        r'(\d+\.?\d*)\s*dollars?',  # 50 dollars
        r'(\d+\.?\d*)\s*USD',       # 50 USD
        r'(\d+\.?\d*)\s*bucks?',    # 50 bucks
        r'(\d+)',                   # Just a number
    ]
    
    amount = None
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            break
    
    if not amount:
        print(f"Mock parser: Could not extract amount from '{text}'")
        return None
    
    print(f"Mock parser: Extracted amount: {amount}")
    
    # Extract date
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # 2025-11-20
        r'(\d{2}/\d{2}/\d{4})',  # 11/20/2025
    ]
    
    date = datetime.now().strftime("%Y-%m-%d")  # Default to today
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            if '/' in date_str:
                # Convert MM/DD/YYYY to YYYY-MM-DD
                parts = date_str.split('/')
                date = f"{parts[2]}-{parts[0]}-{parts[1]}"
            else:
                date = date_str
            break
    
    # Categorize based on keywords
    text_lower = text.lower()
    category = "Other"
    
    if any(word in text_lower for word in ['food', 'grocery', 'groceries', 'restaurant', 'dinner', 'lunch', 'breakfast', 'coffee', 'cafe']):
        category = "Food"
    elif any(word in text_lower for word in ['uber', 'taxi', 'bus', 'train', 'transport', 'gas', 'fuel', 'parking']):
        category = "Transport"
    elif any(word in text_lower for word in ['shop', 'shopping', 'clothes', 'shoes', 'amazon', 'store']):
        category = "Shopping"
    elif any(word in text_lower for word in ['movie', 'cinema', 'entertainment', 'game', 'concert', 'show']):
        category = "Entertainment"
    elif any(word in text_lower for word in ['bill', 'electricity', 'water', 'internet', 'phone', 'rent', 'utility']):
        category = "Bills"
    elif any(word in text_lower for word in ['doctor', 'medicine', 'hospital', 'health', 'pharmacy', 'medical']):
        category = "Health"
    
    # Create description
    description = text.strip()
    
    result = {
        "amount": amount,
        "category": category,
        "date": date,
        "description": description
    }
    
    print(f"Mock parser result: {result}")
    return result
