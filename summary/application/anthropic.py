import anthropic


class ClaudeService:
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

    async def summarize(self, input_text:str , input_prompt:str )->str:
        return self.generate(input_prompt=input_prompt, input_text=input_text)
