import json
import re
import traceback
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from summary.enum.transcript import TargetLanguages

class TranscriptRequest(BaseModel):
    source_language: TargetLanguages = Field(None)
    target_language: List[TargetLanguages] = Field(None)
    history: Optional[List[str]] = Field([""])
    text: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example" : {
                "id" : 1,
                "source_language" : "ko",
                "target_language" : ["en", "zh", "fr", "es"],
                "history": ["안녕하세요."],
                "text" : "오늘 어떻게 도와드릴까요?"
            }
        }

class TranscriptResponse(BaseModel):
    text: str = Field(..., exclude=True)
    source_language: str = Field(...)
    target_language: List[str] = Field([])
    class Config:
        from_attributes = True

    def _verified_response(self, target: str, result: dict) -> dict:
        if not target in result:
            result.update({target: ""})
        else:
            pass
    
    @computed_field
    def result(self) -> str:
        pattern = re.escape(f'(?<="{self.target_language[0]}"\s*:\s*")')
        result = re.search(pattern, self.text)
        import logging
        logger = logging.getLogger("ray.serve")

        logger.warn(f"{pattern} result: {result}")
        return result
    
    @computed_field
    def transcribed(self) -> dict:
        try:
            result = json.loads(self.text)
            self._verified_response("en", result)
            self._verified_response("zh", result)
            self._verified_response("fr", result)
            self._verified_response("ko", result)
            self._verified_response("es", result)
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
