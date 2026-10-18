def transform_news_articles(raw_articles: list[dict]) -> list[dict]:
    """Clean and validate raw news articles."""

    if not raw_articles:
        return []

    required_fields = {"title", "url", "published_at", "source"}

    cleaned_articles = []
    seen_urls = set()

    for article in raw_articles:
        if not isinstance(article, dict):
            continue

        if not required_fields.issubset(article.keys()):
            continue

        title = article.get("title")
        url = article.get("url")

        if not isinstance(title, str) or not title.strip():
            continue

        if not isinstance(url, str) or not url.strip():
            continue

        title = title.strip()
        url = url.strip()

        if url in seen_urls:
            continue

        seen_urls.add(url)

        source = article.get("source")

        if isinstance(source, str):
            source = source.strip() or None
        else:
            source = None

        cleaned_articles.append(
            {
                "title": title,
                "url": url,
                "published_at": article.get("published_at"),
                "source": source,
            }
        )

    return cleaned_articles
