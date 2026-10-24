import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Gemini AI if key exists
API_KEY = os.getenv("GEMINI_API_KEY")
AI_AVAILABLE = False
if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    AI_AVAILABLE = True

def interpret_with_regex(question: str):
    """Deterministic fallback using keywords if AI is unavailable."""
    question = question.lower()
    
    if "total" in question and "revenue" in question:
        return {"intent": "total_revenue", "parameters": {}}
    elif "highest" in question and "product" in question:
        return {"intent": "highest_revenue_product", "parameters": {}}
    elif "trend" in question or "monthly" in question:
        return {"intent": "monthly_revenue_trend", "parameters": {}}
    elif "region" in question or "highest sales" in question:
        return {"intent": "highest_revenue_region", "parameters": {}}
    elif "change" in question or "compare" in question or "between" in question:
        # Default extraction for demo purposes in fallback mode
        return {"intent": "revenue_comparison", "parameters": {"month1": "2026-01", "month2": "2026-02"}}
        
    return {"intent": "unsupported", "parameters": {}}

def interpret_question(question: str):
    """
    Attempts to interpret the question using Gemini AI to return structured JSON.
    Falls back to regex if AI fails or is not configured.
    """
    if not AI_AVAILABLE:
        print("AI unavailable, using Regex fallback.")
        return interpret_with_regex(question)
        
    prompt = f"""
    You are a business intelligence routing assistant.
    Map the following user question to one of these exact intents:
    - total_revenue
    - highest_revenue_product
    - monthly_revenue_trend
    - highest_revenue_region
    - revenue_comparison
    - unsupported (if the question doesn't match the above)
    
    If intent is 'revenue_comparison', extract the two months as YYYY-MM format in a parameters object (month1, month2).
    For example, "January and February 2026" becomes "2026-01" and "2026-02".
    
    Respond ONLY with valid JSON. Do not include markdown formatting like ```json.
    Format: {{"intent": "intent_name", "parameters": {{}}}}
    
    Question: "{question}"
    """
    
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        # Clean up in case the LLM includes markdown
        if text_response.startswith("```json"):
             text_response = text_response[7:-3]
        return json.loads(text_response)
    except Exception as e:
        print(f"AI Interpretation failed: {e}. Using Regex fallback.")
        return interpret_with_regex(question)