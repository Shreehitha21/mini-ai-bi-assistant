# Mini AI Business Intelligence Assistant

A full-stack, AI-assisted business intelligence application built for a Graduate Engineer Trainee (GET) selection assignment. It allows users to ask natural language questions about sales data and receives deterministic, SQL-backed answers.

## 🚀 Public URL
**Deployment Link:** https://mini-ai-bi-assistant.onrender.com/

## 🎯 Features
* **Natural Language to Analytics:** Understands questions like "What is the total revenue?"
* **AI Interpretation with Fallback:** Uses Google Gemini for intent routing, with a seamless Regex fallback if the API is unavailable.
* **Deterministic Analytics:** Never executes raw, untrusted AI-generated SQL. Routes intents to secure, parameterized SQLite queries.
* **Automated Data Quality Checks:** Sanitizes input CSV, handles missing values, and excludes returned/invalid transactions.
* **Clean UI:** Responsive frontend built with HTML, CSS, and Vanilla JS.
* **Robust Testing:** Includes an automated Pytest suite covering all core logic.

## 🛠️ Technology Stack
* **Backend:** Python 3.12, FastAPI, Uvicorn
* **Database:** SQLite (Auto-initialized from CSV via `sqlite3`)
* **Frontend:** HTML, CSS, Vanilla JavaScript
* **AI Integration:** Google Generative AI (Gemini 1.5 Flash)
* **Testing:** Pytest, FastAPI TestClient

## ⚙️ Local Setup Instructions (Windows)

1. **Clone the repository:**
   ```cmd
   git clone <YOUR_GITHUB_REPO_URL>
   cd mini-ai-bi-assistant 

2. **Create and activate a virtual environment:**
   ```cmd
    python -m venv venv
    venv\Scripts\activate

3. **Install dependencies:**
    ```cmd
    pip install -r requirements.txt


4. **Add your Environment Variables:**
    Create a .env file in the root directory:
    ```cmd
    GEMINI_API_KEY=your_gemini_api_key_here
    (Note: The app functions fully via a Regex fallback if no key is provided)

5. **Run the application:**
    ```cmd
    uvicorn app.main:app --reload
    Open a browser and navigate to http://127.0.0.1:8000

6. **Running tests:**
    ```cmd
    pytest -v
