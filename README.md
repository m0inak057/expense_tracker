# AI Expense Tracker

A smart personal expense tracking application built with Django that uses AI to parse natural language expense entries.

## Features

- **Natural Language Parsing**: Simply type "Spent $50 on groceries today" and the AI extracts the amount, category, date, and description.
- **Multiple AI Backends**:
  - **OpenAI**: Uses `gpt-4o-mini` for high-accuracy parsing.
  - **Google Gemini**: Uses Gemini API as a free/cost-effective alternative.
  - **Mock Parser**: A regex-based fallback for offline or free usage.
- **Expense Management**: Track expenses with categories, dates, and descriptions.
- **Receipt Linking**: Support for linking receipt files to expenses.

## Tech Stack

- **Backend**: Django 5.1.3
- **Database**: SQLite (default)
- **AI Integration**: `openai`, `google-generativeai`
- **Environment**: `python-dotenv`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `USE_GEMINI`: Set to "true" to use Google Gemini
   - `USE_MOCK_PARSER`: Set to "true" to force the mock parser

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the server:
   ```bash
   python manage.py runserver
   ```
