from typing import Optional
from pydantic import BaseModel, Field
from app.enum.transcript import TargetLanguages

class SummaryRequest(BaseModel):
    text: str = Field(...)
    prompt_type: str = Field("dental")
    prompt: Optional[str] = Field(None, exclude=True)
    language: Optional[TargetLanguages] = Field(TargetLanguages.ENGLISH)
    

class SummaryResponse(BaseModel):
    text: str

    class Config:
        from_attributes = True
