from pydantic import BaseModel
from typing import Optional


class NewsCreate(BaseModel):
    title: str
    content: str
    language: str
    category: Optional[str] = "Unknown"


class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    language: str
    category: str
    confidence: float