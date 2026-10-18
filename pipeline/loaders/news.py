from .postgres import get_connection


def load_articles(articles: list[dict]) -> int:
    """Insert or update news articles and their embeddings."""

    if not articles:
        print("No articles to load.")
        return 0

    query = """
        INSERT INTO news_articles (
            title, url, published_at, source, embedding
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET
            title = EXCLUDED.title,
            published_at = EXCLUDED.published_at,
            source = EXCLUDED.source,
            embedding = EXCLUDED.embedding;
    """

    rows = [
        (
            article["title"],
            article["url"],
            article.get("published_at"),
            article.get("source"),
            article["vector"],
        )
        for article in articles
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)

    return len(rows)
