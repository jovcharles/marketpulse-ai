from shared.database.connection import get_connection


def search_similar_news(query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Find news articles semantically similar to a given embedding."""

    if not query_embedding:
        return []

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
