ayer Explanations
1. Frontend Layer (Static Files)
Stack: HTML, CSS, Vanilla JS.

Function: Provides the UI. Collects user text inputs and displays structured JSON responses asynchronously using the Fetch API.

2. API Layer (FastAPI)
Stack: FastAPI, Uvicorn, Pydantic.

Function: Exposes RESTful endpoints (/api/ask, /api/data-quality, /health). Validates incoming requests against Pydantic schemas.

Lifecycle Management: Uses FastAPI's lifespan feature to automatically reconstruct the SQLite database from the local sales.csv file upon server startup.

3. NLP Intent Router Layer
Stack: Google Generative AI (Gemini), Python re module.

Function: Acts as a router, not a query writer. It analyzes the user's string and outputs a strict JSON intent (e.g., highest_revenue_product).

Fallback mechanism: If the LLM fails, times out, or has no API key, the system transparently falls back to a deterministic regex/keyword pattern matcher to ensure 100% uptime.

4. Analytics Layer
Function: Maps the interpreted intent to predefined, parameterized Python functions.

Security: Prevents SQL injection and destructive operations by strictly isolating user input from the SQL generation process.

5. Database Layer (SQLite)
Function: Stores tabular sales data.

Data Quality Pipeline: During the initial CSV ingestion, it excludes records with missing prices or zero quantities, and standardizes date formats for accurate temporal queries.