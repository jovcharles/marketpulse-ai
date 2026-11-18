import re
from datetime import date, datetime, timedelta

from backend.app.schemas.query_plan import DateRange, QueryPlan


# Canonical asset mapping: normalized lowercase name/ticker -> database symbol
ASSET_MAPPING: dict[str, str] = {
    "bitcoin": "BTC-USD",
    "btc": "BTC-USD",
    "btc-usd": "BTC-USD",
    "ethereum": "ETH-USD",
    "eth": "ETH-USD",
    "ether": "ETH-USD",
    "eth-usd": "ETH-USD",
    "solana": "SOL-USD",
    "sol": "SOL-USD",
    "sol-usd": "SOL-USD",
    "ripple": "XRP-USD",
    "xrp": "XRP-USD",
    "xrp-usd": "XRP-USD",
    "cardano": "ADA-USD",
    "ada": "ADA-USD",
    "ada-usd": "ADA-USD",
    "dogecoin": "DOGE-USD",
    "doge": "DOGE-USD",
    "doge-usd": "DOGE-USD",
    "avalanche": "AVAX-USD",
    "avax": "AVAX-USD",
    "avax-usd": "AVAX-USD",
    "binance coin": "BNB-USD",
    "bnb": "BNB-USD",
    "bnb-usd": "BNB-USD",
}

# Regex patterns for intent identification
EVENT_ANALYSIS_KEYWORDS = {
    "why",
    "what caused",
    "cause of",
    "reason for",
    "explain",
    "impact of",
    "how come",
}

PRICE_MOVEMENT_KEYWORDS = {
    "crash",
    "drop",
    "dropped",
    "dump",
    "dumped",
    "fall",
    "fell",
    "surge",
    "surged",
    "rally",
    "rallied",
    "spike",
    "spiked",
    "jump",
    "jumped",
    "pump",
    "pumped",
    "plunge",
    "plunged",
    "decline",
    "declined",
}

COMPARISON_KEYWORDS = {
    "compare",
    "comparison",
    "versus",
    "vs",
    "difference between",
    "better than",
    "higher than",
    "outperform",
    "outperformed",
}

NEWS_KEYWORDS = {
    "news",
    "headline",
    "headlines",
    "article",
    "articles",
    "announcement",
    "sentiment",
    "regulation",
    "regulatory",
    "sec",
    "rumor",
    "rumours",
    "coverage",
}

MARKET_LOOKUP_KEYWORDS = {
    "price",
    "prices",
    "cost",
    "value",
    "worth",
    "high",
    "low",
    "open",
    "close",
    "volume",
    "ath",
    "all-time high",
    "market cap",
    "trading at",
    "historical",
    "history",
    "chart",
    "change",
    "moving average",
}

GREETING_OR_GENERAL_PATTERNS = [
    r"^(hi|hello|hey|greetings|howdy)\b",
    r"^who are you\b",
    r"^what can you do\b",
    r"^help\b",
    r"^(what is|explain) (cryptocurrency|blockchain|crypto|bitcoin)\b",
]


def extract_assets(text: str) -> list[str]:
    """Extract and normalize recognized cryptocurrency symbols from text in order of appearance."""
    matches: list[tuple[int, str]] = []
    lowered = text.lower()

    # Sort keys by length descending so multi-word aliases (e.g. "binance coin") take precedence
    matched_spans: list[tuple[int, int]] = []
    for alias, symbol in sorted(
        ASSET_MAPPING.items(), key=lambda item: len(item[0]), reverse=True
    ):
        pattern = r"\b" + re.escape(alias) + r"\b"
        for m in re.finditer(pattern, lowered):
            start, end = m.span()
            # Ensure this match does not overlap an already matched longer alias
            if not any(s <= start < e or s < end <= e for s, e in matched_spans):
                matched_spans.append((start, end))
                matches.append((start, symbol))

    # Sort matches by first appearance in the text
    matches.sort(key=lambda item: item[0])

    found: list[str] = []
    for _, symbol in matches:
        if symbol not in found:
            found.append(symbol)

    return found


def extract_date_range(text: str, reference_date: date | None = None) -> DateRange | None:
    """Extract date range from text using relative or ISO date expressions."""
    ref = reference_date or date.today()
    lowered = text.lower()

    # Relative: today (start = today, end = today + 1 day to satisfy end > start)
    if re.search(r"\btoday\b", lowered):
        return DateRange(start=ref, end=ref + timedelta(days=1))

    # Relative: yesterday
    if re.search(r"\byesterday\b", lowered):
        return DateRange(start=ref - timedelta(days=1), end=ref)

    # Relative: last N days / past N days
    days_match = re.search(r"\b(last|past)\s+(\d+)\s+days?\b", lowered)
    if days_match:
        n = int(days_match.group(2))
        if n > 0:
            return DateRange(start=ref - timedelta(days=n), end=ref)

    # Relative: last week / past week / 7 days
    if re.search(r"\b(last|past)\s+week\b|\blast\s+7\s+days\b", lowered):
        return DateRange(start=ref - timedelta(days=7), end=ref)

    # Relative: last month / past month / 30 days
    if re.search(r"\b(last|past)\s+month\b|\blast\s+30\s+days\b", lowered):
        return DateRange(start=ref - timedelta(days=30), end=ref)

    # Relative: last year / past year
    if re.search(r"\b(last|past)\s+year\b", lowered):
        return DateRange(start=ref - timedelta(days=365), end=ref)

    # Explicit ISO dates: YYYY-MM-DD to YYYY-MM-DD
    range_match = re.search(
        r"(\d{4}-\d{2}-\d{2})\s*(?:to|until|through|-)\s*(\d{4}-\d{2}-\d{2})", lowered
    )
    if range_match:
        try:
            d_start = datetime.strptime(range_match.group(1), "%Y-%m-%d").date()
            d_end = datetime.strptime(range_match.group(2), "%Y-%m-%d").date()
            if d_end > d_start:
                return DateRange(start=d_start, end=d_end)
        except ValueError:
            pass

    # Single explicit ISO date: on YYYY-MM-DD
    single_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", lowered)
    if single_match:
        try:
            d = datetime.strptime(single_match.group(1), "%Y-%m-%d").date()
            return DateRange(start=d, end=d + timedelta(days=1))
        except ValueError:
            pass

    return None


def parse_deterministic_plan(
    question: str, reference_date: date | None = None
) -> QueryPlan | None:
    """
    Attempt to build a deterministic QueryPlan using keyword patterns and entity extraction.
    Returns QueryPlan if confidence is high, or None if ambiguous.
    """
    cleaned = question.strip()
    if not cleaned:
        return QueryPlan(
            original_question=question,
            intent="general_question",
            asset_symbols=[],
            date_range=None,
            retrieval_sources=[],
            semantic_query=None,
        )

    lowered = cleaned.lower()
    assets = extract_assets(cleaned)
    date_range = extract_date_range(cleaned, reference_date=reference_date)

    # Check for general conversational greetings or out-of-scope queries
    for pat in GREETING_OR_GENERAL_PATTERNS:
        if re.search(pat, lowered):
            # If no assets and no financial keywords, classify as general_question
            if not assets and not any(kw in lowered for kw in MARKET_LOOKUP_KEYWORDS):
                return QueryPlan(
                    original_question=cleaned,
                    intent="general_question",
                    asset_symbols=[],
                    date_range=None,
                    retrieval_sources=[],
                    semantic_query=None,
                )

    # Check for Market Event Analysis (Hybrid: SQL + Vector)
    has_event_trigger = any(kw in lowered for kw in EVENT_ANALYSIS_KEYWORDS)
    has_price_movement = any(kw in lowered for kw in PRICE_MOVEMENT_KEYWORDS)
    if has_event_trigger and has_price_movement:
        return QueryPlan(
            original_question=cleaned,
            intent="market_event_analysis",
            asset_symbols=assets,
            date_range=date_range,
            retrieval_sources=["sql", "vector"],
            semantic_query=cleaned,
        )

    # Check for Comparison
    has_comparison = any(kw in lowered for kw in COMPARISON_KEYWORDS)
    if has_comparison or len(assets) > 1:
        # If explicitly comparing or querying multiple assets with price keywords
        if has_comparison or any(kw in lowered for kw in MARKET_LOOKUP_KEYWORDS):
            return QueryPlan(
                original_question=cleaned,
                intent="market_comparison",
                asset_symbols=assets,
                date_range=date_range,
                retrieval_sources=["sql"],
                semantic_query=None,
            )

    # Check for News Search
    has_news = any(kw in lowered for kw in NEWS_KEYWORDS)
    if has_news and not any(kw in lowered for kw in MARKET_LOOKUP_KEYWORDS):
        return QueryPlan(
            original_question=cleaned,
            intent="news_search",
            asset_symbols=assets,
            date_range=date_range,
            retrieval_sources=["vector"],
            semantic_query=cleaned,
        )

    # Check for Market Lookup
    has_market_kw = any(kw in lowered for kw in MARKET_LOOKUP_KEYWORDS)
    if has_market_kw or (assets and date_range):
        return QueryPlan(
            original_question=cleaned,
            intent="market_lookup",
            asset_symbols=assets,
            date_range=date_range,
            retrieval_sources=["sql"],
            semantic_query=None,
        )

    # If assets are mentioned alone (e.g. "Bitcoin", "Tell me about Solana")
    if assets:
        return QueryPlan(
            original_question=cleaned,
            intent="market_lookup",
            asset_symbols=assets,
            date_range=date_range,
            retrieval_sources=["sql"],
            semantic_query=None,
        )

    # Ambiguous - return None to allow LLM fallback
    return None
