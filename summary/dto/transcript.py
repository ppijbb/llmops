import json
import traceback
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from summary.enum.transcript import TargetLanguages

class TranscriptRequest(BaseModel):
    source_language: Optional[TargetLanguages] = Field(None)
    target_language: Optional[List[TargetLanguages]] = Field(None)
    text: str = Field(...)

class TranscriptResponse(BaseModel):
    text: str
    class Config:
        from_attributes = True
        
    @computed_field
    def data(self) -> dict:
        try:
            result = json.loads(self.text)
            result.update({
                "status": "success",
                "detail": "ok"
            })
            return result
        except Exception as e:
            # print(traceback.format_exc())
            print(e)
            result = {
                "status": "error",
                "detail": "failed to parse json"
        }
        finally:
            return result
