import os
import openai
import logging

from summary.application.const import DEFAULT_SUMMARY_FEW_SHOT, DEFAULT_SUMMARY_SYSTEM_PROMPT


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
            input_prompt=input_prompt if input_prompt else DEFAULT_SUMMARY_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content
