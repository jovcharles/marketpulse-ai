from unittest.mock import MagicMock, patch

from pipeline.loaders.news import load_articles


def test_load_articles_uses_news_articles_schema():
    articles = [
        {
            "title": "Bitcoin news",
            "url": "https://example.com/bitcoin",
            "published_at": "2026-10-19T00:00:00Z",
            "source": "Example",
            "vector": [0.1] * 384,
        }
    ]

    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    with patch("pipeline.loaders.news.get_connection") as get_connection:
        get_connection.return_value.__enter__.return_value = connection

        count = load_articles(articles)

    get_connection.assert_called_once_with()
    assert count == 1
    cursor.executemany.assert_called_once()
    query, rows = cursor.executemany.call_args.args
    assert "INSERT INTO news_articles" in query
    assert "source, embedding" in query
    assert "embedding = EXCLUDED.embedding" in query
    assert rows == [
        (
            "Bitcoin news",
            "https://example.com/bitcoin",
            "2026-10-19T00:00:00Z",
            "Example",
            [0.1] * 384,
        )
    ]
