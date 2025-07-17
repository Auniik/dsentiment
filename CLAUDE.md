# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DSentiment is a comprehensive data provider service for sentiment analysis that aggregates content from multiple sources:
- **Gmail API integration** with stateful OAuth authentication for email-based news and content
- **DSE (Dhaka Stock Exchange) stock data APIs** for real-time and historical stock information
- **News content scraping** from major Bangladesh news sources (Prothom Alo, BDNews24, Daily Star)
- **Sentiment analysis integration** (future) for analyzing market sentiment from news and social media

The service provides RESTful APIs for accessing structured data from these sources, enabling sentiment analysis applications to make informed decisions based on market data, news content, and email communications.

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

### Core Components:
1. **OAuth Module** (`/auth/oauth.py`): Handles Google OAuth 2.0 flow with stateful token storage
2. **Email Service** (`/services/email_service.py`): Gmail API integration for email content
3. **DSE Service** (`/services/dse_service.py`): Dhaka Stock Exchange data integration
4. **News Scraper** (`/services/news_scraper.py`): Web scraping for Bangladesh news sources
5. **Token Management** (`/utils/token_storage.py`): File-based token storage and validation
6. **API Routes** (`/api/`): RESTful endpoints for all data sources

### Key API Endpoints:

#### OAuth Authentication:
- `GET /oauth/login?user_email={email}` - Generate Google OAuth URL or check existing token
- `GET /oauth/callback` - Handle OAuth redirect and store token

#### Email APIs:
- `GET /emails?user_email={email}` - Get recent emails for authenticated user
- `GET /emails/search?user_email={email}&query={query}` - Search emails

#### DSE Stock APIs:
- `GET /dse/latest` - List all latest available stocks
- `GET /dse/dsexdata` - Get DSEX data with optional symbol filter
- `GET /dse/top30` - Get top 30 stocks data
- `GET /dse/historical?startDate=2025-07-17&endDate=2025-07-17&inst=1JANATAMF&archive=data` - Get historical stock data using start date and end date by symbol filter

#### News APIs:
- `GET /news/latest` - Get latest news from all sources
- `GET /news/source/{source}` - Get news from specific source (tbsnews, daily-star, bdnews24)
- `GET /news/search?query={query}` - Search news articles
- `GET /news/category/{category}` - Get news by category

## Security Requirements

- **File-based token storage** - Tokens stored securely in local files with hashed user identifiers
- Google credentials loaded from environment variables
- All production endpoints must use HTTPS
- Rate limiting on all endpoints to prevent abuse
- Respect robots.txt and terms of service for web scraping
- User agent rotation and request delays for ethical scraping

## Dependencies

Required packages for implementation:
```toml
dependencies = [
    # FastAPI and server
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "python-multipart>=0.0.6",
    "pydantic>=2.5.0",
    
    # Gmail API (existing)
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "python-dotenv>=1.0.0",
    
    # Stock API web scraping
    "aiohttp>=3.9.1",
    "beautifulsoup4>=4.12.2",
    "lxml>=4.9.3",

    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "feedparser>=6.0.0",
    "newspaper3k>=0.2.8",
    "selenium>=4.15.0",
    "scrapy>=2.11.0",
    "schedule>=1.2.0"
]
```

Development dependencies:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0",
    "black>=23.9.0",
    "isort>=5.12.0",
]
```

## Environment Configuration

Required environment variables:
```bash
# Google OAuth Configuration
GOOGLE_REDIRECT_URI=https://dsetunnel.4nik.com/oauth/callback

# Web Scraping Configuration
SCRAPING_DELAY=2
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
MAX_CONCURRENT_REQUESTS=5

# Application Configuration
APP_ENV=development
LOG_LEVEL=DEBUG
```

## API Scopes and Permissions

### Gmail API Scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access to Gmail

### DSE Data Access:
- Official DSE data portal access
- Third-party API integration
- Web scraping with rate limiting

### News Sources:
- The Business Standard: Web scraping with RSS feeds
- BDNews24: API access and web scraping
- Daily Star: Web scraping and content extraction

## Testing Strategy
- Unit tests for all service modules (Newsflash email, DSE, news scraping)
- Integration tests for OAuth flow and API endpoints
- Mock external API responses for testing
- Test token expiration and refresh scenarios
- Test rate limiting and error handling
- Test web scraping with mock HTML responses
- Performance testing for concurrent requests

## File Structure

```
dsentiment/
├── main.py                # FastAPI application entry point
├── auth/
│   └── oauth.py           # OAuth handling
├── services/
│   ├── email_service.py   # Gmail API integration
│   ├── stock_service.py   # DSE stock data service
│   └── news_scraper.py    # News scraping service
├── scrapers/
│   ├── __init__.py
│   ├── tbsnews.py         # The business standard scraper
│   ├── bdnews24.py        # BDNews24 scraper
│   └── daily_star.py      # Daily Star scraper
├── api/
│   ├── __init__.py
│   ├── oauth.py           # OAuth endpoints
│   ├── emails.py          # Email endpoints
│   ├── dse.py             # DSE stock API endpoints
│   └── news.py            # News API endpoints
├── utils/
│   ├── token_storage.py   # Token storage utilities
│   ├── rate_limiter.py    # Rate limiting utilities
│   └── data_cache.py      # Data caching utilities
├── models/
│   └── schemas.py         # Pydantic models for all services
├── tokens/                # Token storage directory
└── tests/
    ├── test_oauth.py
    ├── test_emails.py
    ├── test_dse.py
    ├── test_news.py
    └── test_scrapers.py
```

## Development Notes

- Follow FastAPI patterns for dependency injection
- Use Pydantic models for request/response validation
- Implement proper error handling for all external API calls
- Add comprehensive logging for debugging all service flows
- Implement rate limiting for all endpoints (especially scraping)
- Use async/await patterns for better performance
- Cache frequently accessed data to reduce API calls
- Implement retry logic for failed requests
- Follow ethical scraping practices (respect robots.txt, rate limits)
- Add proper exception handling for network failures
- Use environment variables for all configuration
- Implement proper data validation and sanitization

## Common Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python main.py

# Run FastAPI server
uv run fastapi dev main.py

# Run tests
uv run pytest

# Run specific test modules
uv run pytest tests/test_dse.py
uv run pytest tests/test_news.py

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy .

# Test scrapers individually
# uv run python -m scrapers.prothom_alo
# uv run python -m scrapers.bdnews24
# uv run python -m scrapers.daily_star
```