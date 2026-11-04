from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DateRange(BaseModel):
    start: date | None = None
    end: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start and self.end and self.end <= self.start:
            raise ValueError("End date must be later than start date")

        return self


class QueryPlan(BaseModel):
    original_question: str

    intent: Literal[
        "market_lookup",
        "news_search",
        "market_event_analysis",
        "market_comparison",
        "general_question",
    ]

    asset_symbols: list[str] = Field(default_factory=list)

    date_range: DateRange | None = None

    retrieval_sources: list[Literal["sql", "vector"]] = Field(default_factory=list)

    semantic_query: str | None = None

    @model_validator(mode="after")
    def validate_retrieval(self):
        if self.intent == "market_event_analysis":
            required = {"sql", "vector"}
            actual = set(self.retrieval_sources)

            if not required.issubset(actual):
                raise ValueError(
                    "Market event analysis requires SQL and vector retrieval"
                )

        if "vector" in self.retrieval_sources and not self.semantic_query:
            raise ValueError("Semantic query is required for vector retrieval")

        return self
