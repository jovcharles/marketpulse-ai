from embeddings.model import model


def embed_news(title: str, description: str = "") -> list[float]:
    text = f"{title}".strip()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()
