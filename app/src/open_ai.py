from pydantic import BaseModel, Field
import os
import logging
from typing import List, Dict,Optional
import json
import sys
import openai
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.src.const import prompt
from app.enum_custom.transcript import TargetLanguages

class TranslationOutput(BaseModel):
    translations: Dict[str, Optional[str]] = Field(default_factory=dict)

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        self.logger = logging.getLogger("ray.serve")
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO)


    def _short_message_for_language(self, target_language: str) -> str:
        if target_language == TargetLanguages.get_language_name(TargetLanguages.CHINESE):
            return "演讲太短了。"
        elif target_language == TargetLanguages.get_language_name(TargetLanguages.ENGLISH):
            return "Speech is too short."
        elif target_language == TargetLanguages.get_language_name(TargetLanguages.KOREAN):
            return "발화가 너무 짧습니다."
        else:
            return "Speech is too short."


    def generate(
        self, 
        input_text: str, 
        input_prompt: str,
        response_model: type[BaseModel] = None
    ):
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "translations": {
                    "type": "object",
                    "description": "Map of language codes to translated text",
                    "additionalProperties": {
                        "type": ["string", "null"]
                    }
                }
            },
            "required": ["translations"]
        }

        completion_params = {
            "model": "gpt-4o-mini",
            "max_tokens": 2048,
            "temperature": 0.6,
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                    {input_prompt}
                    You must respond with JSON that matches this schema.
                    """
                },
                {"role": "user", "content": input_text}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "output",       
                    "schema": schema        
                }
            }
        }

        try:
            result = self.client.chat.completions.create(**completion_params)
            response_content = result.choices[0].message.content
            self.logger.info(f"OpenAI Response: {response_content}")  # 응답 로깅
            json_response = json.loads(response_content)
            return response_model.model_validate(json_response) if response_model else json_response
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Parsing Error: {e}")
            return {"translations": {}}               

        #result = self.client.chat.completions.create(**completion_params)

        # if response_model:
        #     try:
        #         json_response = json.loads(result.choices[0].message.content)
        #         return response_model.model_validate(json_response)
        #     except json.JSONDecodeError as e:
        #         self.logger.error(f"JSON Parsing Error: {e}")
        #         return None
        # return json.loads(result.choices[0].message.content)

        # if response_model:
        #     try:
        #         response_content = result.choices[0].message.content
        #         self.logger.info(f"OpenAI Response: {response_content}")  # 응답 로깅
        #         json_response = json.loads(response_content)
        #         return response_model.model_validate(json_response)
        #     except json.JSONDecodeError as e:
        #         self.logger.error(f"JSON Parsing Error: {e}")
        #         self.logger.error(f"Invalid JSON Response: {response_content}")
        #         return None



    # def generate(
    #     self, 
    #     input_text:str, 
    #     input_prompt:str,
    #     response_model: type[BaseModel] = None
    # ):
    #     return self.client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         max_tokens=2048,
    #         temperature=0.6,
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": input_prompt,
    #             },
    #             {
    #                 "role": "user", 
    #                 "content": input_text
    #             }
    #         ]
    #     )
    
    async def summarize(
        self, 
        input_text:str , 
        input_prompt:str=None
    ) -> str: 
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT_EN, 
            input_text=input_text)
        return result.choices[0].message.content



    async def translate(
        self, 
        input_text: str,
        source_language: str,
        detect_language: str,
        target_language: List[str],
        input_prompt: str = None,
        history: List[str] = [""]
    ) -> Optional[TranslationOutput]:

        generation_prompt = prompt.TRANSLATION_LANGUAGE_PROMPT.format(
            history="\n".join([f"    {h}" for h in history]),
            source=source_language,
            detect=detect_language,
            target=target_language,
            context=" ".join([history[-1] if len(history) > 0 else "", input_text]),
            input_text=input_text
        )

        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSLATION_SYSTEM_PROMPT,
            input_text=generation_prompt,
            response_model=TranslationOutput
        )

        return result.translations

        # #JSON 검증 코드 추가
        # response_content = result.choices[0].message.content
        # try:
        #     parsed_json = json.loads(response_content)  # JSON 변환 시도
        #     print("JSON 변환 성공! Structured Output 정상 작동!")
        #     print(json.dumps(parsed_json, indent=4, ensure_ascii=False))  # JSON 예쁘게 출력
        # except json.JSONDecodeError:
        #     print("JSON 변환 실패! OpenAI가 제대로 JSON을 반환하지 않음.")
        #     print("원본 응답:", response_content)
        #     return None  # JSON 변환 실패 시 None 반환 (또는 예외 처리 가능)


        # translation_output = TranslationOutput.model_validate_json(
        # result.choices[0].message.content
        # )    
        # print(translation_output)
        # return translation_output


    # async def translate(
    #     self, 
    #     input_text:str , 
    #     source_language:str,
    #     detect_language:str,
    #     target_language:List[str], 
    #     input_prompt:str=None,
    #     history:List[str]=[""]
    # ) -> str:
    #     default_system_prompt: str = prompt.DEFAULT_TRANSLATION_SYSTEM_PROMPT
    #     generation_prompt = prompt.TRANSLATION_LANGUAGE_PROMPT.format(
    #         history="\n".join([f"    {h}" for h in history]),
    #         source=source_language,
    #         detect=detect_language, 
    #         target=target_language,
    #         context=" ".join([history[-1] if len(history) > 0 else "", input_text]),
    #         input_text=input_text)
            
    #     result = self.generate(
    #         input_prompt=input_prompt if input_prompt else default_system_prompt, 
    #         input_text=generation_prompt)
    #     return result.choices[0].message.content

        
  
    async def translate_legacy(
        self, 
        input_text:str , 
        source_language:str,
        detect_language:str,
        target_language:List[str], 
        input_prompt:str=None,
        history:List[str]=[""]
    ) -> str:
        default_system_prompt = prompt.LEGACY_MULTI_TRANSLATION_SYSTEM_PROMPT.format(
            lang1=source_language,
            lang2=target_language[0]).strip()
        
        result = self.generate(
            input_prompt=input_prompt if input_prompt else default_system_prompt, 
            input_text=input_text)
        return result.choices[0].message.content
  
    async def translate_summarize(
        self, 
        input_text:str,
        history:List[str],
        source_language:str="ko", 
        target_language:List[str]=["en"],
        input_prompt:str=None,
    ) -> str:
        if len(input_text) < 200:
            return f"**Summary by Transera**\n- {self._short_message_for_language(target_language[0])}"
        else:
            result = self.generate(
                input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT.format(
                    # source=source_language,
                    target=target_language[0]), 
                input_text=f'Target Language={target_language[0]}\n<speech>{input_text}</speech>\n')
            return result.choices[0].message.content