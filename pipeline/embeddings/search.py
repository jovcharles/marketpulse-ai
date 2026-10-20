from embeddings.model import model
from loaders.postgres import get_connection


def search_news(query: str, limit: int = 5) -> list[dict]:
    """Find news articles sematically similar to a search query."""

    if not query.strip():
        return []

    query_embedding = model.encode(
        query.strip(),
        normalize_embeddings=True,
    ).tolist()

    vector = "[" + ",".join(str(value) for value in query_embedding) + "]"

    sql = """
        SELECT
            id,
            title,
            url,
            published_at,
            source,
            1 - (embedding <=> %s::vector) AS similarity
        FROM news_articles
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (vector, vector, limit))
            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "url": row[2],
            "published_at": row[3],
            "source": row[4],
            "similarity": float(row[5]),
        }
        for row in rows
    ]
