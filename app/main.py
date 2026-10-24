from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import contextlib

from app.database import init_db
from app.schemas import AskRequest, AskResponse
from app.question_interpreter import interpret_question
import app.analytics as analytics

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Initializing database from CSV.")
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(title="Mini AI BI Assistant", lifespan=lifespan)



@app.get("/health")
def health_check():
    """Health endpoint to verify API status."""
    return {"status": "ok", "message": "Mini AI BI Assistant is running."}

@app.get("/api/data-quality")
def data_quality_report():
    """Returns import statistics and documented data-quality issues."""
    stats = init_db()
    return {"success": True, "statistics": stats}

@app.post("/api/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """Main endpoint: interprets question, executes SQL, and returns answer."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    interpretation = interpret_question(request.question)
    intent = interpretation.get("intent", "unsupported")
    params = interpretation.get("parameters", {})
    
    response = AskResponse(
        success=True,
        question=request.question,
        intent=intent
    )
    
    try:
        if intent == "total_revenue":
            data, sql = analytics.get_total_revenue()
            response.answer = f"The total revenue is ₹{data['total_revenue']} from {data['transaction_count']} transactions."
            response.supporting_data = data
            response.sql_operation = sql
            
        elif intent == "highest_revenue_product":
            data, sql = analytics.get_highest_revenue_product()
            response.answer = f"The highest revenue product is {data['highest_revenue_product']} with ₹{data['revenue']}."
            response.supporting_data = data['supporting_data']
            response.sql_operation = sql
            
        elif intent == "monthly_revenue_trend":
            data, sql = analytics.get_monthly_revenue_trend()
            response.answer = "Here is the monthly revenue trend."
            response.supporting_data = data
            response.sql_operation = sql
            
        elif intent == "highest_revenue_region":
            data, sql = analytics.get_highest_revenue_region()
            response.answer = f"The {data['highest_revenue_region']} region generated the highest sales with ₹{data['revenue']}."
            response.supporting_data = data['supporting_data']
            response.sql_operation = sql
            
        elif intent == "revenue_comparison":
            m1 = params.get("month1", "2026-01")
            m2 = params.get("month2", "2026-02")
            data, sql = analytics.get_revenue_comparison(m1, m2)
            response.answer = data['explanation']
            response.supporting_data = data
            response.sql_operation = sql
            
        else:
            response.success = False
            response.answer = "I'm sorry, I can only answer questions about total revenue, product revenue, monthly trends, regional sales, and revenue comparisons."
            response.limitations = ["Unsupported question intent."]
            
    except Exception as e:
        response.success = False
        response.error = str(e)
        response.answer = "An error occurred while calculating the results."
        
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_frontend():
    """Serves the frontend HTML file."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))