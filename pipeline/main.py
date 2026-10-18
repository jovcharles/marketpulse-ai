from extractors.market_date import fetch_prices
from loaders.postgres import initialize_database
from loaders.prices import load_prices
from loaders.news import load_articles
from transformations.prices import transform_prices
from transformations.news import transform_news_articles
from extractors.news import fetch_bitcoin_news
from embeddings.news_embeddings import embed_news


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
    loaded_count = load_prices(clean_prices)

    raw_news_articles = fetch_bitcoin_news()

    if not raw_news_articles:
        print("No news articles found. Exiting pipeline.")
        return

    news_articles: list[dict] = transform_news_articles(raw_articles=raw_news_articles)

    for article in news_articles:
        article["vector"] = embed_news(
            title=article["title"],
        )

    article_count = load_articles(news_articles)

    print(
        f"Pipeline completed. Loaded {loaded_count} prices and {article_count} news articles."
    )


run_pipeline()
