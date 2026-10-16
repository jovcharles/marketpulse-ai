from pipeline.extractors.market_date import fetch_prices


def run_pipeline() -> None:
    """Execute the market data ETL workflow"""

    print("Starting MarketPulse AI pipeline...")
    raw_data = fetch_prices(
        symbols=["BTC-USD", "ETH-USD", "SOL-USD"], period="1mo", interval="1d"
    )
    print(raw_data)
    """Connect everything in main.py
Your central entry point will eventually look conceptually like this:

from pipeline.extractors.market_data import fetch_prices
from pipeline.transformers.prices import transform_prices
from pipeline.loaders.prices import load_prices


def run_pipeline():
    raw_data = fetch_prices()

    clean_data = transform_prices(raw_data)

    if clean_data.empty:
        print("No valid records to load.")
        return

    load_prices(clean_data)


if __name__ == "__main__":
    run_pipeline()


Step 6 — Add embeddings later
Once price ingestion works, create a separate news workflow:
1. Fetch financial news.
2. Clean the headline and article text.
3. Save the original article and its metadata.
4. Generate embeddings for new or changed articles.
5. Store the vectors using pgvector.
Embeddings are not part of the price-cleaning workflow. They are a separate processing path because they operate on text rather than numerical price records.
"""
