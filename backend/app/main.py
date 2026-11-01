from fastapi import FastAPI

app = FastAPI(
    title = "MarketPulse AI",
    description = "A pipeline that fetches, transforms, and loads cryptocurrency market data and news articles into a PostgreSQL database.",
    version = "1.0.0"
)


@app.get("/")
def read_root():
    return {"message": "Welcome to MarketPulse AI!"}