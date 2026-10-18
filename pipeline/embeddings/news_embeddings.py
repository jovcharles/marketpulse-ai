from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_news(title: str, description: str = "") -> list[float]:
    text = f"{title}".strip()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()
