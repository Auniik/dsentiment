import os
import json
from typing import Dict, Any, Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.token_storage import TokenStorage


class GoogleOAuthManager:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, client_secret_file: str = "client_secret.json"):
        self.client_secret_file = client_secret_file
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'https://dsetunnel.4nik.com/oauth/callback')
        self.token_storage = TokenStorage()
        
        # Load client configuration from file
        try:
            with open(self.client_secret_file, 'r') as f:
                self.client_config = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Client secret file not found: {self.client_secret_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in client secret file: {self.client_secret_file}")
        
        # Update redirect URI in config
        if "web" in self.client_config:
            self.client_config["web"]["redirect_uris"] = [self.redirect_uri]
        else:
            raise ValueError("Invalid client secret file format: missing 'web' section")
    
    def get_authorization_url(self) -> str:
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to ensure refresh token
        )
        
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user email from the credentials
        try:
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            user_email = profile['emailAddress']
        except Exception as e:
            raise ValueError(f"Failed to get user email: {str(e)}")
        
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'user_email': user_email
        }
        
        return token_data
    
    def validate_token(self, token_data: Dict[str, Any]) -> bool:
        try:
            credentials = Credentials.from_authorized_user_info(token_data)
            
            if credentials.expired:
                print(f"Token expired for user {token_data.get('user_email', 'unknown')}")
                if credentials.refresh_token:
                    print("Attempting to refresh token...")
                    credentials.refresh(Request())
                    return True
                else:
                    print("No refresh token available")
                    return False
            
            print(f"Token valid for user {token_data.get('user_email', 'unknown')}")
            return True
        except Exception as e:
            print(f"Token validation error: {e}")
            return False
    
    def refresh_token(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        credentials = Credentials.from_authorized_user_info(token_data)
        
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
        
        return token_data
    
    def get_user_email(self, token_data: Dict[str, Any]) -> str:
        """Get user email from token"""
        try:
            credentials = Credentials.from_authorized_user_info(token_data)
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build Gmail service to get user info
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        except Exception:
            raise ValueError("Failed to get user email from token")
    
    def get_stored_token(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Get stored token for user"""
        token_data = self.token_storage.load_token(user_email)
        if token_data:
            print(f"Loaded token for user: {user_email}")
            if self.validate_token(token_data):
                # Refresh if needed
                if self._token_needs_refresh(token_data):
                    token_data = self.refresh_token(token_data)
                    self.token_storage.save_token(user_email, token_data)
                return token_data
            else:
                print(f"Token validation failed for user: {user_email}")
                # If token validation fails, delete the invalid token
                self.token_storage.delete_token(user_email)
        else:
            print(f"No token found for user: {user_email}")
        return None
    
    def save_user_token(self, user_email: str, token_data: Dict[str, Any]) -> None:
        """Save token for user"""
        self.token_storage.save_token(user_email, token_data)
    
    def user_has_token(self, user_email: str) -> bool:
        """Check if user has valid stored token"""
        return self.get_stored_token(user_email) is not None
    
    def _token_needs_refresh(self, token_data: Dict[str, Any]) -> bool:
        """Check if token needs refresh"""
        try:
            credentials = Credentials.from_authorized_user_info(token_data)
            return credentials.expired and credentials.refresh_token is not None
        except Exception:
            return False