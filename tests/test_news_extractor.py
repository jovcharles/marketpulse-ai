from pipeline.extractors.news import fetch_bitcoin_news


def test_fetch_bitcoin_news_returns_a_list():
    articles = fetch_bitcoin_news()

    assert isinstance(articles, list)


def test_fetch_bitcoin_news_articles_have_required_fields():
    articles = fetch_bitcoin_news()

    # An empty feed is allowed, but every returned article
    # must contain the fields our extractor promises.
    required_fields = {
        "title",
        "url",
        "published_at",
        "source",
        "description",
    }

    for article in articles:
        assert isinstance(article, dict)
        assert required_fields.issubset(article.keys())
