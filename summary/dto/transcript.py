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
    source_language: str = Field(..., exclude=True)
    target_language: List[str] = Field([], exclude=True)
    class Config:
        from_attributes = True

    def _verified_response(self, target: str, result: dict) -> dict:
        if not target in result:
            result.update({target: ""})
        else:
            pass
    
    @computed_field
    def result(self) -> str:
        # 패턴에 맞는 모든 키-값 쌍 찾기
        pattern = rf'"{re.escape(self.target_language[0])}"\s*:\s*"(.*?)"'
        return re.findall(pattern, self.text)[0]
    
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
