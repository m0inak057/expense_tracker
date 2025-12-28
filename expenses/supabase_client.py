from django.conf import settings
from supabase import create_client, Client
import time

_supabase_client = None

def get_supabase_client(retry=3):
    """Initialize Supabase client with retry mechanism"""
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("ERROR: SUPABASE_URL or SUPABASE_KEY not configured")
        return None
    
    for attempt in range(retry):
        try:
            print(f"Attempting Supabase connection... (attempt {attempt + 1}/{retry})")
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            print("✓ Supabase connected successfully!")
            return _supabase_client
        except Exception as e:
            print(f"✗ Supabase connection error (attempt {attempt + 1}): {e}")
            if attempt < retry - 1:
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                print("ERROR: Failed to connect to Supabase after all retries")
                print("Possible issues:")
                print("1. Check your internet connection")
                print("2. Verify Supabase URL and Key in .env file")
                print("3. Check if Supabase service is up: https://status.supabase.com/")
                return None

supabase = get_supabase_client()
