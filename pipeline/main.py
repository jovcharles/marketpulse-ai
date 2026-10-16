from extractors.market_date import fetch_prices
from transformers.prices import transform_prices


def run_pipeline() -> None:

    print("Starting MarketPulse AI pipeline...")
    raw_data = fetch_prices(
        symbols=["BTC-USD", "ETH-USD", "SOL-USD"], period="1mo", interval="1d"
    )
    transform_prices(raw_data=raw_data)


run_pipeline()
