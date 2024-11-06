import json
import re
import traceback
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field
from summary.enum.transcript import TargetLanguages


class TranslateRequest(BaseModel):
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

class TranslateResponse(BaseModel):
    text: str = Field(..., exclude=True)
    original_text: str = Field(...)
    source_language: str = Field(..., exclude=True)
    target_language: List[str] = Field([], exclude=True)
    class Config:
        from_attributes = True

    def _verified_response(self, target: str, result: dict) -> dict:
        if not target in result:
            result.update({target: ""})
        else:
            pass

    def _as_json(self, target:str) -> dict:
        # 패턴에 맞는 모든 키-값 쌍 찾기
        pattern = rf'"{re.escape(target)}"\s*:\s*"(.*?)"'
        result = re.findall(pattern, self.text)
        return {target: result[0] if len(result) > 0 else ""}
    
    @computed_field
    def result(self) -> str:
        result = list(self._as_json(self.target_language[0]).values())
        return result[0] if len(result) > 0 else self.text
    
    @computed_field
    def translations(self) -> dict:
        try:
            result = json.loads(self.text)
            self._verified_response(TargetLanguages.KOREAN.value, result)
            self._verified_response(TargetLanguages.ENGLISH.value, result)
            self._verified_response(TargetLanguages.CHINESE.value, result)
            self._verified_response(TargetLanguages.FRENCH.value, result)            
            self._verified_response(TargetLanguages.SPANISH.value, result)
            result.update({
                "status": "success",
                "detail": "ok"
            })
        except Exception as e:
            import logging
            logger = logging.getLogger("ray.serve")
            logger.error(self.text)
            result = {
                "status": "error",
                "detail": "failed to parse json. translations parsed from raw text"
            }
            result.update(self._as_json(TargetLanguages.ENGLISH.value))
            result.update(self._as_json(TargetLanguages.CHINESE.value))
            result.update(self._as_json(TargetLanguages.FRENCH.value))
            result.update(self._as_json(TargetLanguages.KOREAN.value))
            result.update(self._as_json(TargetLanguages.SPANISH.value))
            
        finally:
            return result
