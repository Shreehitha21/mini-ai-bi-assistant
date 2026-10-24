# AI Development Report

## 1. Which AI tools I used
I used Google Gemini as an interactive AI coding assistant and technical mentor to guide me through the architecture design, coding, testing, and deployment phases.

## 2. How I used AI during development
I acted as the lead engineer and utilized Gemini to:
* Recommend an appropriate technology stack (FastAPI + SQLite + Vanilla JS) that met all assignment constraints without unnecessary complexity.
* Scaffold boilerplate code (FastAPI routing, HTML layouts).
* Help design a secure AI-interpretation mechanism. Rather than using an unsafe Text-to-SQL approach, the AI suggested using an LLM strictly as an "Intent Router" that triggers predefined, parameterized SQL functions.
* Help write the Pytest automated testing suite.

## 3. Problems encountered
During the automated testing phase, my `test_api.py` suite failed on two specific tests: `test_ask_highest_revenue_product` and `test_ask_highest_revenue_region`. 

## 4. How I debugged them
I captured the standard output from the Pytest failure, which read:
`AssertionError: assert 'highest_revenue_product' in 'The highest revenue product is Monitor with ₹473000.0.'`

I provided this terminal output to the AI. We determined that the test file was mistakenly asserting the presence of the exact snake_case JSON key (`highest_revenue_product`) within the human-readable English answer string. I debugged this by modifying the test file's assertions to check for the correct English substrings (`"highest revenue product" in data["answer"].lower()`), and re-ran the tests successfully.

## 5. What I would improve with another day of work
* **Advanced Visualizations:** Integrate Chart.js or D3.js in the frontend to render dynamic, interactive charts based on the `supporting_data` returned by the API.
* **Agentic Framework (RAG):** If given more time, I would explore integrating LangChain or Google ADK to allow dynamic column discovery, enabling the system to answer arbitrary questions beyond the 5 predefined analytics, while maintaining strict SQL allowlisting.
* **Cloud Database:** Migrate from local SQLite to a persistent PostgreSQL database (e.g., Supabase or Render Postgres) to avoid resetting data upon server restarts.