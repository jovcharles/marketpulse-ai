from .model import get_model


def generate_embedding(text: str) -> list[float]:
    """
    Generate a vector embedding from a text string.
    """
    print(f"Generating embedding for text: '{text}'")
    text = text.strip()

    if not text:
        raise ValueError("Text cannot be empty.")

    model = get_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embedding.tolist()
