from fastapi import FastAPI
from backend.app.routes.news_routes import router as news_router

app = FastAPI(
    title="MarketPulse AI",
    description="A pipeline that fetches, transforms, and loads cryptocurrency market data and news articles into a PostgreSQL database.",
    version="1.0.0",
)


app.include_router(news_router)
