import json
import re
import traceback
import sys
import os
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, computed_field, field_validator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.enum_custom.transcript import TargetLanguages


class SentenceSplitRequest(BaseModel):
    #text: str = Field(...)
    text: str
   
    @field_validator("text", mode="before")
    def clean_text(cls, value: str) -> str:
        """ 
        - 개행 문자를 공백으로 변환
        - 유효하지 않은 제어 문자 제거 (ASCII 코드 0~31 제외, 개행(\n)은 유지)
        """
        if not isinstance(value, str):
            raise ValueError("text 필드는 문자열이어야 합니다.")

        # JSON에서 사용할 수 없는 제어 문자 제거 (개행(\n)은 유지)
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)

        # 개행(\n, \r\n) → 공백(" ")으로 변환
        value = value.replace("\r", "").replace("\n", " ").strip()        
        return value


class SentenceSplitResponse(BaseModel):
    sentences: List[str] = Field(...)


class TranslateRequest(BaseModel):
    source_language: TargetLanguages = Field(None)
    target_language: List[TargetLanguages] = Field(None)
    history: Optional[List[str]] = Field([""])
    text: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example" : {
                "source_language" : "ko",
                "target_language" : ["en", "zh", "fr", "es", "it", "de"],
                "history": ["안녕하세요."],
                "text" : "오늘 어떻게 도와드릴까요?"
            }
        }

class TranslateResponse(BaseModel):
    #text는 에러만 일단 넘김
    text: str = Field(..., exclude=True)
    #original_text: str = Field(...)
    source_language: str = Field(..., exclude=True)
    target_language: List[str] = Field([], exclude=True)
    translations: Dict[str, str] = Field(default_factory=dict)  # 번역 결과 저장
    
    class Config:
        from_attributes = True

    @computed_field
    def result(self) -> str:
        #print("self. target_langunage")
        #print(self.target_language)
        return self.translations.get(self.target_language[0], "")

    def _verified_response(self, target: str, result: dict) -> dict:
        if not target in result:
            result.update({target: ""})
        else:
            pass

    def _as_json(self, text: str) -> dict: #수정
        return json.loads(text)


class TranslateTargetLanguage(BaseModel):
    ko: Optional[str] = Field(None)
    en: Optional[str] = Field(None)
    zh: Optional[str] = Field(None)
    fr: Optional[str] = Field(None)
    es: Optional[str] = Field(None)
    it: Optional[str] = Field(None)
    de: Optional[str] = Field(None)

class TranslateJsonFormat(BaseModel):
    text: str = Field(..., exclude=True)
    source_language: str = Field(..., exclude=True)
    target_language: List[str] = Field([], exclude=True)
    
    original_text: str = Field(...)
    result: str = Field(..., exclude=True)
    translations: TranslateTargetLanguage = Field(...)    


    # def format_as_key_value_pairs(self, text):
    #     # 정규식 변환 수행
    #     formatted_text = re.sub(
    #         r'"([^"]*?)"\s*"([^"]*?)"\s*', 
    #         r'"\1" : "\2", ',
    #         text
    #     )
    #     # 마지막 쉼표 제거
    #     formatted_text = re.sub(
    #         r'(,(|\s+)})',
    #         r"}", 
    #         formatted_text
    #     )
    #     return formatted_text

    # def replace_inner(self, match):
    #     # 매칭된 문자열에서 가장 바깥쪽 "을 제외한 내부의 "를 '로 변환
    #     content = match.group(1)  # 매칭된 문자열
    #     if content is not None:
    #         inner_content = re.sub(
    #             r'(?<!^)"(?!$)', 
    #             "'", 
    #             content
    #         )  # 가장 바깥쪽 " 제외
    #         return f'"{inner_content}"'

    # def _as_json(self, text):
    #     # JSON 형식에서 가장 바깥쪽 ""에 둘러싸인 값 안의 " 를 ' 로 변환
    #     return self.format_as_key_value_pairs(
    #         re.sub(
    #             r'"(.*?)("|",($|\s+|\n+$)|"\s+:|":)(\n+|\s+|\n+$|\s+$)',
    #             self.replace_inner, # 정규식을 사용하여 내부의 "를 '로 변환
    #             text))
    
    # def _parse_to_json(self, target:str) -> dict:
    #     # 패턴에 맞는 모든 키-값 쌍 찾기
    #     _escape = '}'
    #     pattern = rf'"{target}"\s*:\s*"(.*?)("([\s,]*[\s\n]+"|[,\n\s]*{_escape}[\n\s]*$))'
    #     # print(pattern)
    #     # print(self.text)
    #     result = re.search(pattern, self.text)
    #     return {target: result.group(1) if result is not None else ""}
    
    # @computed_field
    # def result(self) -> str:
    #     return self._parse_to_json(self.target_language[0])[self.target_language[0]]
    
    # @computed_field
    # def result(self) -> str:
        
    #     # self.translations가 이미 언어별 번역 결과를 담고 있다고 가정
    #     language_code = self.target_language[0]
    #     #return self.translations.get(language_code, "")
    #     return self.translations.get(language_code, "")
        
    #     #return self.translations.get(self.target_language[0], "")


    # @computed_field
    # def translations(self) -> dict:
    #     try:
    #         print(self._as_json(self.text))
    #         #result = json.loads(self._as_json(self.text))
    #         self._verified_response(TargetLanguages.KOREAN.value, result)
    #         self._verified_response(TargetLanguages.ENGLISH.value, result)
    #         self._verified_response(TargetLanguages.CHINESE.value, result)
    #         self._verified_response(TargetLanguages.FRENCH.value, result)
    #         self._verified_response(TargetLanguages.SPANISH.value, result)
    #         self._verified_response(TargetLanguages.ITALIAN.value, result)            
    #         self._verified_response(TargetLanguages.GERMAN.value, result)
    #         result.update({
    #             "status": "success",
    #             "detail": "ok"
    #         })
    #     except Exception as e:
    #         import logging
    #         logger = logging.getLogger("ray.serve")
    #         logger.error(self.text)
    #         result = {
    #             "status": "error",
    #             "detail": "failed to parse json. translations parsed from raw text"
    #         }
    #         result.update(self._parse_to_json(TargetLanguages.ENGLISH.value))
    #         result.update(self._parse_to_json(TargetLanguages.CHINESE.value))
    #         result.update(self._parse_to_json(TargetLanguages.FRENCH.value))
    #         result.update(self._parse_to_json(TargetLanguages.KOREAN.value))
    #         result.update(self._parse_to_json(TargetLanguages.SPANISH.value))
    #         result.update(self._parse_to_json(TargetLanguages.ITALIAN.value))
    #         result.update(self._parse_to_json(TargetLanguages.GERMAN.value))
            
    #     finally:
    #         return result

    # @computed_field
    # def translations(self) -> Dict[str, str]:
    #     try:
    #         print("translation method called")
    #         print("self.text: ",self.text)

    #         # text가 이미 dict이면 변환할 필요 없음
    #         if isinstance(self.text, str):
    #             try:
    #                 result = json.loads(self.text)  # JSON 문자열을 dict로 변환
    #             except json.JSONDecodeError as e:
    #                 print(f"JSON 디코딩 에러: {e}")
    #                 result = {}  # 변환 실패 시 빈 딕셔너리 반환
    #         else:
    #             result = self.text  # 이미 dict라면 그대로 사용

    #         print("result 통과:", result)  # 변환된 결과 출력
    #         return result

    #     except Exception as e:
    #         print("❌ 번역 처리 중 오류 발생:")
    #         traceback.print_exc()
    #         return {"status": "error", "detail": "번역 처리 실패"}
   

    
    # @computed_field
    # def translations(self) -> dict:
    #     try:
    #         # self.text가 이미 dict라면 바로 사용
    #         print("translation method called")
    #         print(f"self.txt 타입: {type(self.text)}, 값:{self.text}")

    #         result = self.text if isinstance(self.text, dict) else self._as_json(self.text)
            
    #     except Exception as e:
    #         print("실제 오류 메시지: ", e)
    #         #print(f"result타입: {type(result)}, 값:{result}")

    #         for lang in [
    #             TargetLanguages.KOREAN.value,
    #             TargetLanguages.ENGLISH.value,
    #             TargetLanguages.CHINESE.value,
    #             TargetLanguages.FRENCH.value,
    #             TargetLanguages.SPANISH.value,
    #             TargetLanguages.ITALIAN.value,
    #             TargetLanguages.GERMAN.value,
    #         ]:
    #             self._verified_response(lang, result)
    #         result.update({
    #             "status": "success",
    #             "detail": "ok"
    #         })
    #     except Exception as e:
    #         import logging
    #         logger = logging.getLogger("ray.serve")
    #         logger.error(f"번역 파싱 중 에러 발생: {self.text}")
    #         result = {
    #             "status": "error",
    #             "detail": "JSON 파싱 실패. raw text에서 번역 결과를 사용합니다.",
    #             "translations": {}
    #         }
    #     return result
    

# test_data = {
#     "text": '',
#     "original_text": "안녕하세요",
#     "source_language": "ko",
#     "target_language": ["zh","en"],
#     "translations": {"ko": "안녕하세요"}

# }

# # 객체 생성 및 translations 호출
# response = TranslateResponse(**test_data)
# print(response.translations)  # 직접 translations 값 출력
