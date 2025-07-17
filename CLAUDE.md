# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Gmail API integration service that provides stateless OAuth authentication and email access. Users can authenticate with Gmail, download a secure access token, and use that token to access their email data via a RESTful API without server-side token storage.

## Development Environment

### Package Management
- Use `uv` for dependency management and virtual environment handling
- Python 3.12+ required
- Project configuration is in `pyproject.toml`

### Common Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python main.py

# Run FastAPI server (when implemented)
uv run fastapi dev main.py

# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy .
```

## Architecture Overview

The application follows a modular FastAPI architecture:

### Core Components (to be implemented):
1. **OAuth Module** (`/auth/oauth.py`): Handles Google OAuth 2.0 flow
2. **Email Service** (`/services/email_service.py`): Gmail API integration
3. **Token Management** (`/utils/token_utils.py`): Token validation and handling
4. **API Routes** (`/api/`): RESTful endpoints for OAuth and email operations

### Key API Endpoints:
- `GET /oauth/login` - Generate Google OAuth URL
- `GET /oauth/callback` - Handle OAuth redirect and return token.json
- `POST /emails` - Accept token and return recent emails

## Security Requirements

- **No server-side token storage** - All tokens are client-managed
- Google credentials loaded from environment variables
- All production endpoints must use HTTPS
- Rate limiting on email endpoints recommended

## Dependencies to Add

Required packages for implementation:
```toml
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "python-multipart>=0.0.6",
    "pydantic>=2.0.0"
]
```

Development dependencies:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "httpx>=0.25.0"  # for testing
]
```

## Environment Configuration

Required environment variables:
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth callback URL

## Gmail API Scopes

The application uses read-only Gmail access:
- `https://www.googleapis.com/auth/gmail.readonly`

## Testing Strategy

- Unit tests for token validation and email parsing
- Integration tests for OAuth flow
- Mock Gmail API responses for testing
- Test token expiration and refresh scenarios

## File Structure (Recommended)

```
dsentiment/
├── main.py                 # FastAPI application entry point
├── auth/
│   └── oauth.py           # OAuth handling
├── services/
│   └── email_service.py   # Gmail API integration
├── api/
│   ├── __init__.py
│   ├── oauth.py           # OAuth endpoints
│   └── emails.py          # Email endpoints
├── utils/
│   └── token_utils.py     # Token validation utilities
├── models/
│   └── schemas.py         # Pydantic models
└── tests/
    ├── test_oauth.py
    └── test_emails.py
```

## Development Notes

- Follow FastAPI patterns for dependency injection
- Use Pydantic models for request/response validation
- Implement proper error handling for OAuth failures
- Add logging for debugging OAuth flows
- Consider implementing request rate limiting for production