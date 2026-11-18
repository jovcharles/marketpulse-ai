from datetime import datetime

from shared.database.connection import get_connection


def search_similar_news(
    query_embedding: list[float],
    limit: int = 5,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[dict]:

    if not query_embedding:
        return []

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    vector = "[" + ",".join(str(value) for value in query_embedding) + "]"

    conditions = ["embedding IS NOT NULL"]
    params = []

    if start_date is not None:
        conditions.append("published_at >= %s")
        params.append(start_date)

    if end_date is not None:
        conditions.append("published_at < %s")
        params.append(end_date)

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            id,
            title,
            url,
            published_at,
            source,
            1 - (embedding <=> %s::vector) AS similarity
        FROM news_articles
        WHERE {where_clause}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """

    params = [vector, *params, vector, limit]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
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
