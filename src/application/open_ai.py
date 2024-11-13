import os
import logging
from typing import List

import openai

from src.application.const import prompt


class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ["OPENAI_API_KEY"])

    def generate(
        self, 
        input_text:str, 
        input_prompt:str
    ):
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": input_prompt,
                },
                {
                    "role": "user", 
                    "content": input_text
                }
            ]
        )

    async def summarize(
        self, 
        input_text:str , 
        input_prompt:str=None
    ) -> str:
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content

    async def translate(
        self, 
        input_text:str , 
        source_language:str,
        detect_language:str,
        target_language:List[str], 
        input_prompt:str=None,
        history:List[str]=[""]
    ) -> str:
        default_system_prompt: str = prompt.DEFAULT_TRANSLATION_SYSTEM_PROMPT
        default_system_prompt += prompt.TRANSLATION_LANGUAGE_PROMPT.format(
            history="\n".join([f"\t{h}" for h in history]),
            source=source_language,
            detect=detect_language, 
            target=target_language)
        
        result = self.generate(
            input_prompt=input_prompt if input_prompt else default_system_prompt, 
            input_text=input_text)
        return result.choices[0].message.content
  
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
            lang2=target_language[0])
        
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
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT.format(
                source=source_language,
                target=target_language[0]), 
            input_text=f'<speech>{input_text}</speech>')
        return result.choices[0].message.content
      