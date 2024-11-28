from typing import Optional
from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    prompt: Optional[str] = Field(None)
    text: str = Field(...)

class SummaryResponse(BaseModel):
    text: str

    class Config:
        from_attributes = True
