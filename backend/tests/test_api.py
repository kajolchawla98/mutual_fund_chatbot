from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Mutual Fund Chatbot API"}

def test_advisory_refusal():
    response = client.post(
        "/chat/query",
        json={"session_id": "test_1", "user_message": "Should I invest in HDFC Mid-cap?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_flag"] is True
    assert "I am a facts-only assistant" in data["answer_text"]

def test_performance_refusal():
    response = client.post(
        "/chat/query",
        json={"session_id": "test_2", "user_message": "What were the returns in 1 year for ICICI?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_flag"] is True
    assert "analyze or predict historical fund performance" in data["answer_text"]

def test_out_of_scope_refusal():
    response = client.post(
        "/chat/query",
        json={"session_id": "test_3", "user_message": "What is the best way to cook pasta?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_flag"] is True
    assert "limited to specific factual information" in data["answer_text"]

def test_sanitization(mocker):
    # Mocking the classifier so we don't actually trigger real DB/LLM flows
    mocker.patch('app.services.classifier.QueryClassifier.classify_intent', return_value="FACTUAL")
    # Mock vector search to return empty to trigger safe fallback (we just want to check input didn't crash)
    response = client.post(
        "/chat/query",
        json={"session_id": "test_4", "user_message": "My PAN is ABCDE1234F, what is the exit load?"}
    )
    assert response.status_code == 200
    # If the input processed correctly without crashing, sanitization didn't break it
