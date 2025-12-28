from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .supabase_client import supabase
from .ai_parser import parse_expense


def home(request):
    """Render the main frontend page"""
    return render(request, 'index.html')


def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        "message": "Welcome to AI Expense Tracker API",
        "endpoints": {
            "add_expense": "/expenses/add/ [POST]",
            "list_expenses": "/expenses/list/<user_id>/ [GET]"
        }
    })


def health(request):
    """Lightweight health check endpoint for uptime/cron pings.

    Returns overall status plus a simple Supabase client status. This is
    intentionally cheap so it can be called frequently by Render cron.
    """
    db_status = "not_configured"

    if supabase is not None:
        db_status = "client_initialized"

    payload = {
        "status": "ok",
        "database": db_status,
        "timestamp": timezone.now().isoformat(),
    }

    return JsonResponse(payload)

@csrf_exempt
def add_expense(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        # Check if direct data or text parsing
        if "text" in data:
            # Old AI parsing method
            user_id = data.get("user_id")
            text = data.get("text")
            
            if not user_id or not text:
                return JsonResponse({"error": "Missing user_id or text"}, status=400)

            parsed = parse_expense(text)
            if not parsed:
                return JsonResponse({"error": "Parsing failed. Check server logs for details."}, status=400)

            expense_data = {
                "user_id": user_id,
                "amount": float(parsed["amount"]),
                "category": str(parsed["category"]),
                "date": parsed["date"],
                "description": str(parsed["description"]),
                "raw_text": text
            }
        else:
            # Direct form data (new method)
            user_id = data.get("user_id")
            amount = data.get("amount")
            category = data.get("category")
            date = data.get("date")
            description = data.get("description")
            
            # Validate required fields
            if not all([user_id, amount, category, date, description]):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            # Validate amount is numeric
            try:
                amount = float(amount)
                if amount <= 0:
                    return JsonResponse({"error": "Amount must be greater than 0"}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid amount"}, status=400)
            
            expense_data = {
                "user_id": user_id,
                "amount": amount,
                "category": category,
                "date": date,
                "description": description,
                "raw_text": None
            }

        try:
            if supabase is None:
                error_msg = "Database connection failed. Please check: 1) Internet connection 2) Supabase credentials in .env 3) Supabase service status"
                return JsonResponse({"error": error_msg}, status=500)
            
            expense = supabase.table("expenses").insert(expense_data).execute()
            return JsonResponse({"status": "success", "data": expense.data})
        except ConnectionError as e:
            print(f"Network connection error: {str(e)}")
            return JsonResponse({"error": "Network error: Cannot connect to database. Check your internet connection."}, status=503)
        except Exception as e:
            print(f"Database error: {str(e)}")
            error_type = type(e).__name__
            if "11001" in str(e) or "getaddrinfo" in str(e):
                return JsonResponse({"error": "Network error: Cannot reach Supabase. Check your internet connection or firewall settings."}, status=503)
            return JsonResponse({"error": f"Database error ({error_type}): {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def list_expenses(request, user_id):
    if supabase is None:
        return JsonResponse({"error": "Database connection not available"}, status=500)
    
    try:
        result = supabase.table("expenses") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("date", desc=True) \
            .execute()

        return JsonResponse(result.data, safe=False)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)


@csrf_exempt
def scan_receipt(request):
    """Scan receipt using Gemini Vision AI - instant, no downloads!"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_data_url = data.get("image")
            
            if not image_data_url:
                return JsonResponse({"error": "No image data provided"}, status=400)
            
            # Use Gemini Vision to scan receipt
            from .gemini_vision import scan_receipt_with_gemini
            
            print("Scanning receipt with Gemini Vision AI...")
            result = scan_receipt_with_gemini(image_data_url)
            
            return JsonResponse({
                "status": "success",
                "data": result
            })
            
        except Exception as e:
            print(f"Receipt scanning error: {str(e)}")
            return JsonResponse({
                "error": f"Receipt scanning failed: {str(e)}"
            }, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
