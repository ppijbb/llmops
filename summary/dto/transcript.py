import json
import traceback
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from summary.enum.transcript import TargetLanguages

class TranscriptRequest(BaseModel):
    source_language: TargetLanguages = Field(None)
    target_language: List[TargetLanguages] = Field(None)
    text: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example" : {
                "id" : 1,
                "source_language" : "ko",
                "target_language" : ["en", "zh", "fr", "es"],
                "text" : "안녕하세요, 오늘 어떻게 도와드릴까요?"
            }
        }

class TranscriptResponse(BaseModel):
    text: str
    class Config:
        from_attributes = True

    @computed_field
    def transcribed(self) -> dict:
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
