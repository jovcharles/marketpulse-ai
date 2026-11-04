from shared.embeddings.model import get_model
from shared.embeddings.service import generate_embedding


def embed_news(title: str, description: str = "") -> list[float]:
    text = f"{title}".strip()
    model = get_model()
    embedding = generate_embedding(text)
    return embedding.tolist()
