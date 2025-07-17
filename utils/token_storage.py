import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path


class TokenStorage:
    def __init__(self, storage_dir: str = "tokens"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_user_hash(self, user_email: str) -> str:
        """Create a hash of user email for filename"""
        return hashlib.sha256(user_email.encode()).hexdigest()[:16]
    
    def _get_token_file_path(self, user_email: str) -> Path:
        """Get the file path for user's token"""
        user_hash = self._get_user_hash(user_email)
        return self.storage_dir / f"token_{user_hash}.json"
    
    def save_token(self, user_email: str, token_data: Dict[str, Any]) -> None:
        """Save user token to file"""
        token_file = self._get_token_file_path(user_email)
        
        # Add user email to token data for reference
        token_data_with_user = {
            **token_data,
            "user_email": user_email
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data_with_user, f, indent=2)
    
    def load_token(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Load user token from file"""
        token_file = self._get_token_file_path(user_email)
        
        if not token_file.exists():
            return None
        
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            return token_data
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def delete_token(self, user_email: str) -> bool:
        """Delete user token file"""
        token_file = self._get_token_file_path(user_email)
        
        if token_file.exists():
            token_file.unlink()
            return True
        return False
    
    def token_exists(self, user_email: str) -> bool:
        """Check if user has a stored token"""
        token_file = self._get_token_file_path(user_email)
        return token_file.exists()
    
    def list_users(self) -> list[str]:
        """List all users with stored tokens"""
        users = []
        for token_file in self.storage_dir.glob("token_*.json"):
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    if "user_email" in token_data:
                        users.append(token_data["user_email"])
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        return users