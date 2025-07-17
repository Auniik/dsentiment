from fastapi import APIRouter, HTTPException, Query
from auth.oauth import GoogleOAuthManager
from services.email_service import GmailService
from models.schemas import EmailsResponse, ErrorResponse

router = APIRouter(prefix="/emails", tags=["emails"])

oauth_manager = GoogleOAuthManager()


@router.get("", response_model=EmailsResponse)
async def get_emails(
    user_email: str = Query(..., description="User email address"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of emails to return")
):
    """
    Fetch recent emails using stored token for user
    """
    try:
        # Get stored token for user
        token_data = oauth_manager.get_stored_token(user_email)
        if not token_data:
            raise HTTPException(
                status_code=401, 
                detail=f"No valid token found for user {user_email}. Please authenticate first."
            )
        
        gmail_service = GmailService(token_data)
        emails = gmail_service.get_recent_emails(max_results=max_results)
        
        return EmailsResponse(emails=emails, count=len(emails))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


@router.get("/search", response_model=EmailsResponse)
async def search_emails(
    user_email: str = Query(..., description="User email address"),
    query: str = Query(..., description="Gmail search query"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of emails to return")
):
    """
    Search emails using Gmail query syntax with stored token
    """
    try:
        # Get stored token for user
        token_data = oauth_manager.get_stored_token(user_email)
        if not token_data:
            raise HTTPException(
                status_code=401, 
                detail=f"No valid token found for user {user_email}. Please authenticate first."
            )
        
        gmail_service = GmailService(token_data)
        emails = gmail_service.search_emails(query=query, max_results=max_results)
        
        return EmailsResponse(emails=emails, count=len(emails))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search emails: {str(e)}")