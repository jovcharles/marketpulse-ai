from shared.embeddings.service import generate_embedding
from backend.app.repositories.news_repository import search_similar_news


def search_news(query: str, limit: int = 5) -> list[dict]:

    query = query.strip()
    print(f"Searching for news articles with query: '{query}' and limit: {limit}")
    if not query:
        raise ValueError("Query cannot be empty")

    query_embedding = generate_embedding(query)

    if not query_embedding:
        raise ValueError("Failed to generate embedding for the query")

    results = search_similar_news(query_embedding, limit)

    return results
