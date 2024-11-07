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
    
    def _as_json(self, text):
        # JSON 형식에서 가장 바깥쪽 ""에 둘러싸인 값 안의 " 를 ' 로 변환
        def format_as_key_value_pairs(self, text):
            # 정규식 변환 수행
            formatted_text = re.sub(
                r'"([^"]*?)"\s*"([^"]*?)"\s*', 
                r'"\1" : "\2", ',
                text
            )
            # 마지막 쉼표 제거
            formatted_text = re.sub(
                r'(,(|\s+)})',
                r"}", 
                formatted_text
            )
            return formatted_text

        def replace_inner(self, match):
            # 매칭된 문자열에서 가장 바깥쪽 "을 제외한 내부의 "를 '로 변환
            content = match.group(1)  # 매칭된 문자열
            if content is not None:
                inner_content = re.sub(
                    r'(?<!^)"(?!$)', 
                    "'", 
                    content
                )  # 가장 바깥쪽 " 제외
                return f'"{inner_content}"'
    
        # 정규식을 사용하여 내부의 "를 '로 변환
        return format_as_key_value_pairs(
            re.sub(
                r'"(.*?)("|",($|\s+|\n+$)|"\s+:|":)(\n+|\s+|\n+$|\s+$)',
                replace_inner, 
                text))
    
    def _parse_to_json(self, target:str) -> dict:
        # 패턴에 맞는 모든 키-값 쌍 찾기
        _escape = '}'
        pattern = rf'"{target}"\s*:\s*"(.*?)"(,\s+\n+|{re.escape(_escape)}*$)'
        result = re.search(pattern, self.text)
        return {target: result if len(result) > 0 else ""}
    
    @computed_field
    def result(self) -> str:
        result = list(self._parse_to_json(self.target_language[0]).values())
        return result[0] if len(result) > 0 else self.text
    
    @computed_field
    def translations(self) -> dict:
        try:
            result = json.loads(self._as_json(self.text))
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
            result.update(self._parse_to_json(TargetLanguages.ENGLISH.value))
            result.update(self._parse_to_json(TargetLanguages.CHINESE.value))
            result.update(self._parse_to_json(TargetLanguages.FRENCH.value))
            result.update(self._parse_to_json(TargetLanguages.KOREAN.value))
            result.update(self._parse_to_json(TargetLanguages.SPANISH.value))
            
        finally:
            return result
