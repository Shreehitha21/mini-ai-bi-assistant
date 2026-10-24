import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import init_db

client = TestClient(app)

def setup_module(module):
    print("Initializing test database...")
    init_db()

def test_health_check():
    """Test 1: Does the application start up and report healthy?"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Mini AI BI Assistant is running."}

def test_data_quality_endpoint():
    """Test 2: Does the data quality endpoint return the expected statistics?"""
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["statistics"]["rows_processed"] == 51
    assert data["statistics"]["successfully_imported"] == 49
    assert data["statistics"]["rejected_rows"] == 2

def test_ask_total_revenue():
    """Test 3: Can the API handle the 'total revenue' question correctly?"""
    response = client.post(
        "/api/ask",
        json={"question": "What is the total revenue?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "total_revenue"
    assert "total_revenue" in data["supporting_data"]
    assert "SELECT" in data["sql_operation"]

def test_ask_highest_revenue_product():
    """Test 4: Can the API handle the 'highest revenue product' question?"""
    response = client.post(
        "/api/ask",
        json={"question": "Which product generated the highest revenue?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "highest_revenue_product"
    
    assert "highest revenue product" in data["answer"].lower() 
    assert isinstance(data["supporting_data"], list)

def test_ask_monthly_trend():
    """Test 5: Can the API handle the 'monthly trend' question?"""
    response = client.post(
        "/api/ask",
        json={"question": "What is the monthly revenue trend?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "monthly_revenue_trend"
    assert "month_labels" in data["supporting_data"]

def test_ask_highest_revenue_region():
    """Test 6: Can the API handle the 'highest sales region' question?"""
    response = client.post(
        "/api/ask",
        json={"question": "Which region generated the highest sales?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "highest_revenue_region"
    
    assert "generated the highest sales" in data["answer"].lower()

def test_ask_revenue_comparison():
    """Test 7: Can the API handle a revenue comparison question?"""
    response = client.post(
        "/api/ask",
        json={"question": "How did revenue change between January and February 2026?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "revenue_comparison"
    assert "absolute_change" in data["supporting_data"]
    assert "percentage_change" in data["supporting_data"]

def test_unsupported_question():
    """Test 8: Does the application safely reject unsupported questions?"""
    response = client.post(
        "/api/ask",
        json={"question": "What is the capital of France?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["intent"] == "unsupported"
    assert "I can only answer questions about" in data["answer"]
    assert len(data["limitations"]) > 0

def test_empty_question():
    """Test 9: Does the API handle empty questions correctly?"""
    response = client.post(
        "/api/ask",
        json={"question": "   "}
    )
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]