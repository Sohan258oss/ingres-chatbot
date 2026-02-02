import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to sys.path to allow importing Backend.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.main import app
from Backend.data_manager import KNOWLEDGE_BASE, TIPS, WHY_MAP

# Mock the indices loading/building to avoid API calls during startup
patch('Backend.retriever.HybridRetriever.load_indices', return_value=True).start()
patch('Backend.retriever.HybridRetriever.build_indices').start()

@patch('Backend.retriever.HybridRetriever.search')
@patch('Backend.reranker.Reranker.rerank')
def test_knowledge_base_query(mock_rerank, mock_search):
    mock_search.return_value = [{"name": "aquifer", "score": 0.9, "index": "concepts"}]
    mock_rerank.return_value = [{"name": "aquifer", "score": 0.9, "rerank_score": 0.95, "index": "concepts"}]

    with TestClient(app) as client:
        response = client.post("/ask", json={"message": "What is an aquifer?"})
        assert response.status_code == 200
        data = response.json()
        assert "aquifer" in data["text"].lower()
        # Join chunks for comparison
        full_def = " ".join(KNOWLEDGE_BASE["aquifer"])
        assert full_def in data["text"]

@patch('Backend.retriever.HybridRetriever.search')
@patch('Backend.reranker.Reranker.rerank')
def test_location_query(mock_rerank, mock_search):
    mock_search.return_value = [{"name": "Karnataka", "score": 0.9, "index": "locations"}]
    mock_rerank.return_value = [{"name": "Karnataka", "score": 0.9, "rerank_score": 0.95, "index": "locations"}]

    with TestClient(app) as client:
        response = client.post("/ask", json={"message": "Karnataka groundwater"})
        assert response.status_code == 200
        data = response.json()
        assert "Karnataka" in data["text"]
        assert "extraction" in data["text"].lower()

@patch('Backend.retriever.HybridRetriever.search')
@patch('Backend.reranker.Reranker.rerank')
def test_news_fallback(mock_rerank, mock_search):
    mock_search.return_value = []
    mock_rerank.return_value = []

    with TestClient(app) as client:
        response = client.post("/ask", json={"message": "Who won the world cup?"})
        assert response.status_code == 200
        data = response.json()
        assert "latest groundwater updates" in data["text"].lower()

@patch('Backend.retriever.HybridRetriever.search')
@patch('Backend.reranker.Reranker.rerank')
def test_why_query(mock_rerank, mock_search):
    mock_search.return_value = [{"name": "punjab", "score": 0.9, "index": "causes"}]
    mock_rerank.return_value = [{"name": "punjab", "score": 0.9, "rerank_score": 0.95, "index": "causes"}]

    with TestClient(app) as client:
        response = client.post("/ask", json={"message": "why Punjab"})
        assert response.status_code == 200
        data = response.json()
        assert "Punjab" in data["text"]
        assert WHY_MAP["punjab"] in data["text"]

@patch('Backend.retriever.HybridRetriever.search')
@patch('Backend.reranker.Reranker.rerank')
def test_master_plan_query(mock_rerank, mock_search):
    mock_search.return_value = [{"name": "master plan", "score": 0.9, "index": "concepts"}]
    mock_rerank.return_value = [{"name": "master plan", "score": 0.9, "rerank_score": 0.95, "index": "concepts"}]

    with TestClient(app) as client:
        response = client.post("/ask", json={"message": "master plan"})
        assert response.status_code == 200
        data = response.json()
        assert "Master Plan" in data["text"]
        assert "1.42 crore" in data["text"]
