from fastapi import FastAPI
from dotenv import load_dotenv
from api.oauth import router as oauth_router
from api.emails import router as emails_router
from api.dse import router as dse_router

load_dotenv()

app = FastAPI(
    title="Sentiment Analysis APIs",
    description="APIs for sentiment analysis using Gmail API, OpenAI, Scrapped news and other services.",
    version="0.1.0"
)

app.include_router(oauth_router)
app.include_router(emails_router)
app.include_router(dse_router)

@app.get("/")
async def root():
    return {"message": "Sentiment Analysis APIs", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8991, log_level="debug")
