import anthropic

from app.src.const import prompt
from app.src.service._base import BaseNLPService

class ClaudeService(BaseNLPService):
    def __init__(self):
        self.client = anthropic.Anthropic()

    def generate(self, input_text:str , input_prompt:str ):
        return self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system=input_prompt,
            messages=[
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

    async def transcript(self, input_text:str , input_prompt:str=None):
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSCRIPT_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content
  
    async def transcript_summarize(self, input_text:str , input_prompt:str=None):
        result = self.generate(
            input_prompt=input_prompt if input_prompt else prompt.DEFAULT_TRANSCRIPT_SUMMARIZE_SYSTEM_PROMPT, 
            input_text=input_text)
        return result.choices[0].message.content
