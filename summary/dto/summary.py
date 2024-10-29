from typing import Optional, List
from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    prompt: Optional[str] = Field(None)
    text: str = Field(...)

class SummaryResponse(BaseModel):
    text: str

    class Config:
        from_attributes = True
        
class TranscriptRequest(BaseModel):
    source_language: str = Field(...)
    target_language: List[str] = Field(...)
    text: str = Field(...)
    