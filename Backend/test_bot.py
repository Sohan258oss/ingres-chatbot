import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the current directory to sys.path to allow importing Backend.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.main import app, KNOWLEDGE_BASE, TIPS, WHY_MAP

def test_knowledge_base_query():
    with TestClient(app) as client:
        # Semantic search for a knowledge base key
        response = client.post("/ask", json={"message": "aquifer"})
        assert response.status_code == 200
        data = response.json()
        assert "aquifer" in data["text"].lower()
        assert KNOWLEDGE_BASE["aquifer"] in data["text"]

def test_location_query():
    with TestClient(app) as client:
        # Semantic search for a location
        response = client.post("/ask", json={"message": "Karnataka"})
        assert response.status_code == 200
        data = response.json()
        assert "Karnataka" in data["text"]
        assert "extraction" in data["text"].lower()

def test_news_fallback():
    with TestClient(app) as client:
        # Query that should have low confidence (< 0.65)
        response = client.post("/ask", json={"message": "Who won the world cup?"})
        assert response.status_code == 200
        data = response.json()
        assert "latest groundwater updates" in data["text"].lower()

def test_why_query():
    with TestClient(app) as client:
        # "Why" query matching WHY_MAP
        response = client.post("/ask", json={"message": "why Punjab"})
        assert response.status_code == 200
        data = response.json()
        assert "Punjab" in data["text"]
        assert WHY_MAP["punjab"] in data["text"]

def test_master_plan_query():
    with TestClient(app) as client:
        # Query for one of the newly added 50 QA pairs
        response = client.post("/ask", json={"message": "master plan"})
        assert response.status_code == 200
        data = response.json()
        assert "Master Plan" in data["text"]
        assert "1.42 crore" in data["text"]
