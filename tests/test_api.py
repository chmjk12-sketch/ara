"""ARA - API Endpoint Tests"""
import pytest
import respx
from tests.conftest import client


@respx.mock
def test_analyze_endpoint(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "房价为什么下跌？"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "intent" in data["data"]
    assert "depth" in data["data"]
    assert data["data"]["intent"] == "Reality"
    assert data["data"]["depth"] == "Level1"


@respx.mock
def test_analyze_decision(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "计算机专业值得读吗？"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["intent"] == "Decision"


@respx.mock
def test_analyze_optimization(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "产品增长停滞了怎么办？"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["intent"] == "Optimization"


@respx.mock
def test_analyze_innovation(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "现在有什么创业机会？"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["intent"] == "Innovation"


@respx.mock
def test_depth_escalation(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "详细分析房价未来10年"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["depth"] == "Level2"


@respx.mock
def test_depth_full_report(client):
    response = client.post(
        "/api/v1/analyze",
        json={"message": "给我一份完整房地产研究报告"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["depth"] == "Level3"


@respx.mock
def test_mcp_tools(client):
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
