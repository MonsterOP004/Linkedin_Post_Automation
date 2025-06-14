from pydantic import BaseModel, Field
from typing import Optional, Literal


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

class ImageAnalysisOutput(BaseModel):
    description: str
    key_elements: list[str]
    sentiment: str

class VideoAnalysisOutput(BaseModel):
    summary: str
    key_moments: list[str]
    sentiment: str

class URLAnalysisOutput(BaseModel):
    summary: str
    main_points: list[str]
    tone_of_source: str
