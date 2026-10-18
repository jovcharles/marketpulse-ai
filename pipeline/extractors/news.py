import feedparser

NEWS_URL = "https://news.google.com/rss/search" "?q=Bitcoin&hl=en-US&gl=US&ceid=US:en"


def fetch_bitcoin_news() -> list[dict]:
    """Fetch Bitcoin-related articles from Google News RSS."""

    feed = feedparser.parse(NEWS_URL)

    if feed.bozo and not feed.entries:
        raise RuntimeError(
            f"Failed to parse Google News RSS: " f"{feed.bozo_exception}"
        )

    articles = []

    for entry in feed.entries:
        articles.append(
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "published_at": entry.get("published"),
                "source": entry.get("source", {}).get("title"),
            }
        )
    return articles


fetch_bitcoin_news()
