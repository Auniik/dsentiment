from typing import List, Dict, Any
from pydantic import BaseModel, Field


class AuthUrlResponse(BaseModel):
    auth_url: str = Field(..., description="Google OAuth authorization URL")


class TokenRequest(BaseModel):
    token: Dict[str, Any] = Field(..., description="Gmail access token data")


class EmailData(BaseModel):
    id: str = Field(..., description="Email message ID")
    sender: str = Field(..., description="Email sender address")
    subject: str = Field(..., description="Email subject")
    snippet: str = Field(..., description="Email snippet/preview")
    date: str = Field(..., description="Email date")


class EmailsResponse(BaseModel):
    emails: List[EmailData] = Field(..., description="List of email messages")
    count: int = Field(..., description="Number of emails returned")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str = Field(None, description="Detailed error information")