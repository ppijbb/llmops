import os
import openai


class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, input_text:str , input_prompt:str ):
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
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

    async def summarize(self, input_text:str , input_prompt:str )->str:
        result = self.generate(input_prompt=input_prompt, input_text=input_text)
        return result.choices[0].message.content
