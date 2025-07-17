import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app
from models.schemas import EmailData

client = TestClient(app)


@patch('api.emails.oauth_manager')
@patch('api.emails.GmailService')
def test_get_emails_success(mock_gmail_service, mock_oauth_manager):
    mock_oauth_manager.validate_token.return_value = True
    
    mock_email_data = [
        EmailData(
            id="1",
            sender="test@example.com",
            subject="Test Subject",
            snippet="Test snippet",
            date="2024-01-01 12:00:00"
        )
    ]
    
    mock_service_instance = Mock()
    mock_service_instance.get_recent_emails.return_value = mock_email_data
    mock_gmail_service.return_value = mock_service_instance
    
    token_request = {
        "token": {
            "token": "mock_token",
            "refresh_token": "mock_refresh_token"
        }
    }
    
    response = client.post("/emails", json=token_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert "count" in data
    assert data["count"] == 1
    assert len(data["emails"]) == 1


@patch('api.emails.oauth_manager')
def test_get_emails_invalid_token(mock_oauth_manager):
    mock_oauth_manager.validate_token.return_value = False
    mock_oauth_manager.refresh_token.return_value = {"token": "invalid"}
    
    token_request = {
        "token": {
            "token": "invalid_token"
        }
    }
    
    response = client.post("/emails", json=token_request)
    
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


@patch('api.emails.oauth_manager')
@patch('api.emails.GmailService')
def test_search_emails_success(mock_gmail_service, mock_oauth_manager):
    mock_oauth_manager.validate_token.return_value = True
    
    mock_email_data = [
        EmailData(
            id="1",
            sender="test@example.com",
            subject="Search Result",
            snippet="Search result snippet",
            date="2024-01-01 12:00:00"
        )
    ]
    
    mock_service_instance = Mock()
    mock_service_instance.search_emails.return_value = mock_email_data
    mock_gmail_service.return_value = mock_service_instance
    
    token_request = {
        "token": {
            "token": "mock_token",
            "refresh_token": "mock_refresh_token"
        }
    }
    
    response = client.post("/emails/search?query=test", json=token_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert "count" in data
    assert data["count"] == 1