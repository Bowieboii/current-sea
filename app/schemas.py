"""The JSON shapes accepted and returned by the API."""

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10_000,
        description="Text to inspect for wording that may need clarification.",
        examples=["We should send it soon."],
    )


class AmbiguitySignal(BaseModel):
    code: str
    category: str
    phrase: str
    start: int
    end: int
    explanation: str
    clarification_question: str


class ScanResponse(BaseModel):
    request_id: str
    asset_id: str
    asset_version: str
    source: str
    daily_limit: int = Field(ge=1)
    daily_remaining: int = Field(ge=0)
    method: str
    ambiguous: bool
    ambiguity_score: int = Field(ge=0, le=100)
    signal_count: int
    signals: list[AmbiguitySignal]
    limitation: str


class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    development_stage: str
