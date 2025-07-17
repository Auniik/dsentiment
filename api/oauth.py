from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from auth.oauth import GoogleOAuthManager
from models.schemas import AuthUrlResponse, ErrorResponse

router = APIRouter(prefix="/oauth", tags=["oauth"])

oauth_manager = GoogleOAuthManager()


@router.get("/login")
async def get_login_url(user_email: str = Query(None, description="User email address")):
    """
    Check if user has valid token, if not generate Google OAuth login URL
    """
    try:
        # If no user_email provided, always redirect to auth
        if not user_email:
            auth_url = oauth_manager.get_authorization_url()
            return JSONResponse(
                content={
                    "auth_url": auth_url,
                    "has_token": False,
                    "message": "Please authenticate using the provided URL"
                }
            )
        
        # Check if user already has a valid token
        if oauth_manager.user_has_token(user_email):
            return JSONResponse(
                content={
                    "message": "User already authenticated",
                    "has_token": True,
                    "user_email": user_email
                }
            )
        
        # Generate auth URL if no valid token exists
        auth_url = oauth_manager.get_authorization_url()
        return JSONResponse(
            content={
                "auth_url": auth_url,
                "has_token": False,
                "user_email": user_email,
                "message": "Please authenticate using the provided URL"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process login request: {str(e)}")


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(None, description="State parameter for CSRF protection")
):
    print(f"OAuth callback received with code: {code}, state: {state}")
    """
    Handle OAuth callback, store token, and return success message
    """
    try:
        # Exchange code for token
        token_data = oauth_manager.exchange_code_for_token(code)

        print(token_data)
        
        # Get user email from token data
        user_email = token_data.get('user_email')
        if not user_email:
            raise ValueError("User email not found in token data")
        
        # Save token to file storage
        oauth_manager.save_user_token(user_email, token_data)
        
        return JSONResponse(
            content={
                "message": "Authentication successful! Token saved.",
                "user_email": user_email,
                "status": "success"
            }
        )
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")


@router.get("/token/{user_email}")
async def get_user_token(user_email: str):
    """
    Get stored token for user (for debugging purposes)
    """
    try:
        token_data = oauth_manager.get_stored_token(user_email)
        if token_data:
            # Remove sensitive data for response
            safe_token_data = {
                "user_email": user_email,
                "has_token": True,
                "scopes": token_data.get("scopes", [])
            }
            return JSONResponse(content=safe_token_data)
        else:
            return JSONResponse(
                content={
                    "user_email": user_email,
                    "has_token": False,
                    "message": "No valid token found for user"
                },
                status_code=404
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token: {str(e)}")