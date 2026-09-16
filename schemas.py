from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    unanswered_questions: list[str] = Field(default_factory=list)
