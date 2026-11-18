import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are the MarketPulse AI Query Planner.
Your job is to analyze the user's question about cryptocurrency markets and output a JSON execution plan.

Supported intents:
- "market_lookup": For numerical price, volume, high/low, or OHLCV queries on assets. retrieval_sources: ["sql"].
- "news_search": For sentiment, news, articles, regulation, or general announcements. retrieval_sources: ["vector"].
- "market_event_analysis": For questions asking WHY an asset moved or explaining crashes/surges (requires both price data and news). retrieval_sources: ["sql", "vector"].
- "market_comparison": Comparing metrics across two or more assets. retrieval_sources: ["sql"].
- "general_question": Conversational, greetings, or non-crypto questions. retrieval_sources: [].

Canonical asset symbols: BTC-USD, ETH-USD, SOL-USD, XRP-USD, ADA-USD, DOGE-USD, AVAX-USD, BNB-USD.
Date range format: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} where end > start, or null.
If "vector" is in retrieval_sources, semantic_query MUST be a non-empty string.

Respond ONLY with valid JSON matching this schema:
{
  "intent": "<intent>",
  "asset_symbols": ["<symbol>"],
  "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} or null,
  "retrieval_sources": ["sql"] | ["vector"] | ["sql", "vector"] | [],
  "semantic_query": "<query or null>"
}
"""


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_plan(self, question: str) -> dict[str, Any] | None:
        """Analyze a question and return a raw dictionary matching QueryPlan fields."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Mock provider for unit tests and offline development."""

    def __init__(self, plan_to_return: dict[str, Any] | None = None):
        self._plan_to_return = plan_to_return

    def set_plan(self, plan: dict[str, Any] | None) -> None:
        self._plan_to_return = plan

    def generate_plan(self, question: str) -> dict[str, Any] | None:
        if self._plan_to_return is not None:
            return self._plan_to_return
        # Default fallback
        return {
            "intent": "general_question",
            "asset_symbols": [],
            "date_range": None,
            "retrieval_sources": [],
            "semantic_query": None,
        }


class OllamaProvider(BaseLLMProvider):
    """Provider connecting to a local Ollama instance."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 5.0,
    ):
        self.base_url = (
            base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.timeout = timeout

    def generate_plan(self, question: str) -> dict[str, Any] | None:
        endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload)
                if response.status_code != 200:
                    logger.warning(
                        f"Ollama returned status {response.status_code}: {response.text}"
                    )
                    return None

                data = response.json()
                content = data.get("message", {}).get("content", "")
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
                return None
        except Exception as e:
            logger.warning(f"Failed to query Ollama LLM provider: {e}")
            return None


def get_llm_provider() -> BaseLLMProvider | None:
    """Factory to retrieve configured LLM provider from environment."""
    provider_name = os.getenv("LLM_PROVIDER", "deterministic").lower()

    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "mock":
        return MockLLMProvider()
    elif provider_name in ("none", "deterministic"):
        return None

    return None
