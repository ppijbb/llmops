import torch
import ray
import psutil
from typing import List
import numpy as np
from transformers import GenerationConfig

from summary.depend import get_model


# ray.init(
#     num_cpus=psutil.cpu_count(logical=True), 
#     ignore_reinit_error=True,
#     )


# @ray.remote
class LLMService(object):
    default_bos: str = "<|begin_of_text|>"
    default_eot: str = "<|eot_id|>"
    default_start_header: str = "<|start_header_id|>"
    default_end_header: str = "<|end_header_id|>"

    def __init__(self):
        self.model, self.tokenizer = get_model(
            # model_path="meta-llama/Meta-Llama-3-8B",  # GPU (vllm) Model
            model_path="fakezeta/llama-3-8b-instruct-ov-int8", # CPU Model
            adapter_path=None,
            inference_tool="ov")
        
        self.bos_token = self.tokenizer.bos_token if self.tokenizer.bos_token else self.default_bos
        self.eot_token = self.tokenizer.eos_token if self.tokenizer.eos_token else self.default_eot
        self.start_header = self.default_start_header
        self.end_header = self.default_end_header

    def _template_header(self, role:str = "role") -> str:
        return f'{self.start_header}{role}{self.end_header}\n\n'

    def get_prompt(self,
                   user_input: str, 
                   chat_history: list[tuple[str, str]],
                   system_prompt: str = "") -> str:
        prompt_texts = [f"{self.bos_token}"]
        chat_template = self._template_header() + '{prompt}' + self.eot_token +'\n\n'
        generate_template = chat_template + self._template_header(role="assistant")
        
        def template_dict(role, prompt):
            return { "role": role, "prompt": prompt }
        
        if system_prompt != '':
            prompt_texts.append(chat_template.format(role="system", prompt=system_prompt))
            # prompt_texts.append(template_dict(role="system", prompt=system_prompt))

        for history_input, history_response in chat_history:
            prompt_texts.append(chat_template.format(role="user", prompt=history_input.strip()))
            # prompt_texts.append(template_dict(role="user", prompt=history_input.strip()))
            prompt_texts.append(chat_template.format(role="assistant", prompt=history_response.strip()))
            # prompt_texts.append(template_dict(role="assistant", prompt=history_response.strip()))

        prompt_texts.append(chat_template.format(role="user", prompt=user_input.strip()))
        # prompt_texts.append(template_dict(role="user", prompt=user_input.strip()))

        return "".join(prompt_texts) if not isinstance(prompt_texts[0], dict) else prompt_texts
    

    def formatting(self, prompt: List[str] | List[dict]):
        if isinstance(prompt, str):
            return self.tokenizer(prompt, return_tensors="pt")
        else:
            return { "input_ids":self.tokenizer.apply_chat_template(prompt, return_tensors="pt") }

    @torch.inference_mode()
    def _make_summary(self,
                      input_text: str) -> str:
        chat_template = {
            "user_input": input_text,
            "chat_history": [],
            "system_prompt": "summarize dialogue. your job is summarizing dialouge in korean language. summarize in 3 sentecens."
        }
        prompt = self.get_prompt(**chat_template)
        if torch.cuda.is_available(): # vllm generation
            output = self.model.generate(prompt)
            output_str= output[0].outputs[0].text
        else: # ipex, ov generation
            inputs = self.formatting(prompt=prompt)
            output = self.model.generate(**inputs,
                                         do_sample=True,
                                        #  temperature=0.6,
                                         max_length=4096,
                                         top_p=0.9,
                                         use_cache=True,)
            output_str = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return output_str.replace(". ", ".\n")
    
    @torch.inference_mode()
    def generate_stream(self, prompt, max_length=50):
        input_ids = self.tokenizer.encode(prompt, return_tensors="np")
        
        for _ in range(max_length):
            outputs = self.model([input_ids])[self.model.output(0)]
            next_token_logits = outputs[0, -1, :]
            next_token = np.argmax(next_token_logits)
            
            if next_token == self.tokenizer.eos_token_id:
                break
            
            input_ids = np.concatenate([input_ids, [[next_token]]], axis=-1)
            
            yield self.tokenizer.decode([next_token], skip_special_tokens=True)

        
    def summarize(self, input_text: str) -> str:
        return self._make_summary(input_text)


llm_service = LLMService()

async def get_llm_service():
    # yield LLMService.remote()
    yield llm_service
