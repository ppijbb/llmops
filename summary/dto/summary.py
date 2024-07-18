from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    text: str = Field(...)

class SummaryResponse(BaseModel):
    text: str

    class Config:
        from_attributes = True