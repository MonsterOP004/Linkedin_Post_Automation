from pydantic import BaseModel, Field


class CriticOutput(BaseModel):
    clarity: int = Field(..., ge=1, le=10)
    tone: int = Field(..., ge=1, le=10)
    engagement: int = Field(..., ge=1, le=10)
    relevance: int = Field(..., ge=1, le=10)
    suggestion: str


class WriterOutput(BaseModel):
    content: str


class ResearchOutput(BaseModel):
    summary: str
