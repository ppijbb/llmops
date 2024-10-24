import torch
import ray
import psutil
import logging
from typing import List
import numpy as np
from transformers import GenerationConfig
from transformers.generation.streamers import TextIteratorStreamer
from threading import Thread

from summary.depend import get_model, get_claude, get_gpt
from summary.application.const import DEFAULT_SUMMARY_FEW_SHOT, DEFAULT_SUMMARY_SYSTEM_PROMPT

# ray.init(
#     num_cpus=psutil.cpu_count(logical=True), 
#     ignore_reinit_error=True,
#     )

# @ray.remote
class LLMService(object):
    default_bos: str = "<|begin_of_text|>"
    default_eot: str = "<|end_of_text|>"
    llama_start_header: str = "<|start_header_id|>"
    llama_end_header: str = "<|end_header_id|>"
    mistral_start_header: str = "[INST]"
    mistral_end_header: str = "[/INST]"

    def __init__(self):
        self.model, self.tokenizer = get_model(
            # model_path="KISTI-KONI/KONI-Llama3-8B-Instruct-20240729", # GPU (vllm) Model
            model_path="Gunulhona/Llama-Merge-Small",  # GPU (vllm) Model
            # model_path="fakezeta/llama-3-8b-instruct-ov-int8",
            # model_path="Gunulhona/openvino-llama-3-ko-8B_int8",
            # model_path="Gunulhona/openvino-llama-3.1-8B_int8", # CPU Model
            adapter_path=None,
            inference_tool="ov")
        self.text_streamer = TextIteratorStreamer(
            self.tokenizer, 
            skip_prompt=True, 
            skip_special_tokens=True)
        
        self.bos_token = self.tokenizer.bos_token if self.tokenizer.bos_token else self.default_bos
        self.eot_token = "<|eot_id|>"#self.tokenizer.eos_token if self.tokenizer.eos_token else self.default_eot
        if not  torch.cuda.is_available():
            self.start_header = self.llama_start_header if "llama" in self.model.config.model_type else self.mistral_start_header
            self.end_header = self.llama_end_header if "llama" in self.model.config.model_type else self.mistral_end_header
        else:
            self.start_header = self.llama_start_header
            self.end_header = self.llama_end_header
        self.max_new_tokens = 500

    def _template_header(self, role:str = "{role}") -> str:
        return f'{self.start_header}{role}{self.end_header}\n'

    def get_prompt(self,
                   user_input: str, 
                   chat_history: list[tuple[str, str]] =[],
                   system_prompt: str = "") -> str:
        prompt_texts = [f"{self.bos_token}"]
        chat_template = self._template_header() + '{prompt}' + self.eot_token +'\n'
        generate_template = chat_template + self._template_header(role="assistant")
        
        def template_dict(role, prompt):
            return { "role": role, "prompt": prompt }
        
        if system_prompt != '':
            prompt_texts.append(chat_template.format(role="system", prompt=system_prompt.strip()))
            # prompt_texts.append(template_dict(role="system", prompt=system_prompt))

        for history_role, history_response in chat_history:
            # print(history_role, history_response)
            prompt_texts.append(chat_template.format(role=history_role, prompt=history_response.strip()))
            # prompt_texts.append(template_dict(role=history_role, prompt=history_reponse.strip()))

        prompt_texts.append(generate_template.format(role="user", prompt=user_input.strip()))
        # prompt_texts.append(template_dict(role="user", prompt=user_input.strip()))

        return "".join(prompt_texts) if not isinstance(prompt_texts[0], dict) else prompt_texts
    

    def formatting(self, prompt: List[str] | List[dict], return_tensors: str = "pt") -> dict:
        if isinstance(prompt, str):
            return self.tokenizer(prompt, return_tensors=return_tensors)
        else:
            return { "input_ids": self.tokenizer.apply_chat_template(prompt, return_tensors=return_tensors) }

    def generate_config(self, **kwargs):
        generation_config = dict(
            do_sample=True,
            temperature=0.6,
            max_new_tokens=self.max_new_tokens,
            penalty_alpha=0.5,
            no_repeat_ngram_size=5,
            top_p=0.9,
            use_cache=True)
        generation_config.update(kwargs)
        return generation_config

    def vllm_generate_config(self, **kwargs):
        from vllm.sampling_params import SamplingParams
        return SamplingParams(
            repetition_penalty=1.0,
            frequency_penalty=1.0,
            presence_penalty=1.0,
            temperature=0.3,
            top_p=0.9,
            max_tokens=self.max_new_tokens)

    @torch.inference_mode()
    def _make_summary(self,
                      input_text: str,
                      input_prompt: str = None,
                      input_history: List[str] = [],
                      use_fewshot: bool = False) -> str:
        chat_template = {
            "user_input": input_text,
            "chat_history": DEFAULT_SUMMARY_FEW_SHOT if len(input_history) == 0 and use_fewshot else input_history,
            "system_prompt": DEFAULT_SUMMARY_SYSTEM_PROMPT if input_prompt is None else input_prompt
            }
        prompt = self.get_prompt(**chat_template)
        if torch.cuda.is_available(): # vllm generation
            from vllm.sampling_params import SamplingParams
            output = self.model.generate(prompt, sampling_params=self.vllm_generate_config(), use_tqdm=False)
            output_str= output[0].outputs[0].text
        else: # ipex, ov generation
            inputs = self.formatting(prompt=prompt)
            output = self.model.generate(**self.generate_config(**inputs))
            output_str = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        return output_str.replace(". ", ".\n")
    
    @torch.inference_mode()
    def generate_stream(self, input_text: str, input_prompt: str = None):
        if input_prompt is not None:
            input_text = input_prompt + "\n" + input_text
        inputs = self.formatting(prompt=input_text.strip(), return_tensors="pt")
        inputs.update(dict(streamer=self.text_streamer))
        thread = Thread(
            target=self.model.generate, 
            kwargs=self.generate_config(**inputs))
        thread.start()
        for new_text in self.text_streamer:
            yield new_text

    @torch.inference_mode()
    def generate_stream_cuda(self, input_text: str, input_prompt: str = None):
        # inputs = self.formatting(prompt=prompt , return_tensors="pt")
        response = self._make_summary(input_text=input_text, input_prompt=input_prompt)
        for new_text in response:
            yield new_text

    @torch.inference_mode()
    def _raw_generate(self, prompt: str, max_length: int = 4096):
        input_ids = self.formatting(prompt=prompt, return_tensors="pt")["input_ids"]
        for _ in range(max_length):
            outputs = self.model(input_ids=input_ids)[0]
            next_token = torch.unsqueeze(torch.unsqueeze(torch.argmax(outputs[0, -1, :]), 0),1)
            if next_token == self.tokenizer.eos_token_id:
                break
            input_ids = torch.concatenate([input_ids, next_token], axis=-1)
            yield self.tokenizer.decode(next_token[0], skip_special_tokens=True)

    def summarize(self, input_text: str, input_prompt: str = None, stream: bool = False):
        if torch.cuda.is_available() and stream:
            return self.generate_stream_cuda(input_text=input_text, input_prompt=input_prompt)
        elif stream:
            return self.generate_stream(input_text=input_text, input_prompt=input_prompt)
        else:
            return self._make_summary(input_text=input_text, input_prompt=input_prompt)


llm_service = LLMService()

async def get_llm_service():
    # yield LLMService.remote()
    yield llm_service

async def get_gpt_service():
    yield get_gpt()

async def get_claude_service():
    yield get_claude()
