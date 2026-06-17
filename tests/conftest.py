"""ARA - Test Configuration"""
import pytest
import respx


@pytest.fixture
def app():
    from src.main import app
    return app


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)
