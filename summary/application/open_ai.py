import os
import logging
from typing import List

import openai

from summary.application.const import prompt


class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, input_text:str , input_prompt:str ):
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2048,
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

    async def summarize(self, input_text:str , input_prompt:str=None):
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content

    async def transcript(self, input_text:str , source_language:str, target_language:List[str], input_prompt:str=None):
        default_system_prompt: str = prompt.DEFAULT_TRANSCRIPT_SYSTEM_PROMPT
        default_system_prompt += prompt.TRANSCRIPTION_LANGUAGE_PROMPT.format(source=source_language, target=target_language)
        result = self.generate(
            input_prompt=input_prompt if input_prompt else default_system_prompt, 
            input_text=input_text)
        return result.choices[0].message.content
  
    async def transcript_summarize(self, input_text:str , input_prompt:str=None):
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSCRIPT_SUMMARIZE_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content
      