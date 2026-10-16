from extractors.market_date import fetch_prices
from pipeline.loaders.postgres import initialize_database
from transformers.prices import transform_prices


def run_pipeline() -> None:

    print("Starting MarketPulse AI pipeline...")
    raw_prices = fetch_prices(
        symbols=["BTC-USD", "ETH-USD", "SOL-USD"], period="1mo", interval="1d"
    )
    clean_prices = transform_prices(raw_data=raw_prices)

    if clean_prices.empty:
        print("No valid prices found. Exiting pipeline.")
        return

    initialize_database()


run_pipeline()
