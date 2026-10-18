from pipeline.embeddings.news_embeddings import embed_news

embedding = embed_news(
    "Bitcoin price surges to new all-time high",
    "The price of Bitcoin has reached a new all-time high, surpassing previous records and attracting attention from investors and the media alike.",
)

assert (
    len(embedding) == 384
), "Embedding length should be 384 for the 'all-MiniLM-L6-v2' model."

print("Embedding generated successfully!")

print("Dimensions:", len(embedding))
