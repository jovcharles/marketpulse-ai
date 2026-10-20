from pipeline.embeddings.search import search_news


def test_search_news_returns_a_list():
    results = search_news("Bitcoin price movements and cryptocurrency market news")

    assert isinstance(results, list)
