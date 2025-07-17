import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@patch('api.oauth.oauth_manager')
def test_get_login_url(mock_oauth_manager):
    mock_oauth_manager.get_authorization_url.return_value = "https://accounts.google.com/oauth/authorize?..."
    
    response = client.get("/oauth/login")
    
    assert response.status_code == 200
    assert "auth_url" in response.json()
    assert response.json()["auth_url"].startswith("https://accounts.google.com")


@patch('api.oauth.oauth_manager')
def test_oauth_callback_success(mock_oauth_manager):
    mock_token_data = {
        "token": "mock_token",
        "refresh_token": "mock_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    }
    mock_oauth_manager.exchange_code_for_token.return_value = mock_token_data
    
    response = client.get("/oauth/callback?code=mock_code&state=mock_state")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers["content-disposition"]


@patch('api.oauth.oauth_manager')
def test_oauth_callback_failure(mock_oauth_manager):
    mock_oauth_manager.exchange_code_for_token.side_effect = Exception("OAuth failed")
    
    response = client.get("/oauth/callback?code=invalid_code")
    
    assert response.status_code == 400
    assert "OAuth callback failed" in response.json()["detail"]