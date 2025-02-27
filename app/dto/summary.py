from typing import Optional
from pydantic import BaseModel, Field
from app.enum.transcript import TargetLanguages

class SummaryRequest(BaseModel):
    prompt: Optional[str] = Field(None)
    text: str = Field(...)
    language: Optional[TargetLanguages] = Field(TargetLanguages.ENGLISH)

class SummaryResponse(BaseModel):
    text: str

    class Config:
        from_attributes = True
