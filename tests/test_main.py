import pytest
from app import create_app

# Pytest fixture to create and configure a new app instance for each test
@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

# Pytest fixture to provide a test client for sending HTTP requests
@pytest.fixture
def client(app):
    return app.test_client()

# Test the index route to ensure correct status code and response content
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    # Check that the expected content appears in the response
    assert b'Hello, World!' in response.data
    assert b'Welcome to our Agile Web App' in response.data
