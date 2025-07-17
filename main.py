from fastapi import FastAPI
from dotenv import load_dotenv
from api.oauth import router as oauth_router
from api.emails import router as emails_router

load_dotenv()

app = FastAPI(
    title="Gmail API Integration",
    description="Stateless Gmail OAuth integration with token management",
    version="0.1.0"
)

app.include_router(oauth_router)
app.include_router(emails_router)


@app.get("/")
async def root():
    return {"message": "Gmail API Integration Service", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8991, log_level="debug")
