import torch
import logging
import subprocess
from typing import List
from itertools import zip_longest

from fastapi import FastAPI
from contextlib import asynccontextmanager
import numpy as np
from fastapi import FastAPI
from transformers import GenerationConfig
from transformers.generation.streamers import TextIteratorStreamer
from threading import Thread
from ray import serve

from app.depend import get_model, get_claude, get_gpt
from app.src.const import prompt
from app.src.const.select_domain import select_summary_domain
from app.src.service._base import BaseNLPService

from app.src.service.anthropic import ClaudeService
from app.src.service.open_ai import OpenAIService


@asynccontextmanager
async def llm_ready(app: FastAPI):
    # TODO : make llm load once in linespan
    yield

async def get_llm_service():
    yield LLMService()

async def get_gpt_service():
    yield get_gpt()

async def get_claude_service():
    yield get_claude()

def get_accelerator():
    resources = {
        "num_cpus": 1.0,
        "memory": 1024,
        "runtime_env": {
            "env_vars": {
                "NEURON_CC_FLAGS": "-O1"
                }
            }
        }
    if torch.cuda.is_available():
        resources.update({"num_gpus": 0.1})
    elif subprocess.run(["neuron-ls"], shell=True).returncode == 0:
        resources.update({"resources": {"neuron_cores": 2.0}})
    else:
        pass
    return resources


class GenerationService(BaseNLPService):
    default_bos: str = "<|begin_of_text|>"
    default_eot: str = "<|end_of_text|>"
    llama_start_header: str = "<|start_header_id|>"
    llama_end_header: str = "<|end_header_id|>"
    mistral_start_header: str = "[INST]"
    mistral_end_header: str = "[/INST]"
    gemma_start_header: str = "<start_of_turn>"
    gemma_end_header: str = "<end_of_turn>"
    
    def __init__(
        self,
        *args,
        **kwargs
    ):
        self.model, self.tokenizer = get_model(
            # model_path="KISTI-KONI/KONI-Llama3-8B-Instruct-20240729", # GPU (vllm) Model
            # model_path="google/gemma-2-2b-it",  # GPU (vllm) Model
            model_path="Gunulhona/Gemma-System-9B-MoRA-SimPO-AWQ",
            # model_path="hugging-quants/gemma-2-9b-it-AWQ-INT4",
            # model_path="unsloth/gemma-2-2b-it-bnb-4bit",
            # model_path="AIFunOver/gemma-2-2b-it-openvino-8bit", # CPU Model
            # model_path="Gunulhona/Llama-Merge-Small",  # GPU (vllm) Model
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
        self.eot_token = self.tokenizer.eos_token if self.tokenizer.eos_token else self.default_eot
        if torch.cuda.is_available():
            self.local_model_type = self.model.llm_engine.model_config.hf_text_config.model_type
        else:
            self.local_model_type = self.model.config.model_type

        match self.local_model_type:
            case "llama":
                self.start_header = self.llama_start_header 
                self.end_header = self.llama_end_header
            case "gemma2":
                self.start_header = self.gemma_start_header
                self.end_header = self.gemma_end_header
            case "mistral":
                self.start_header = self.mistral_start_header
                self.end_header = self.mistral_end_header
            case _:
                self.local_model_type = 'llama'
                self.start_header = self.llama_start_header
                self.end_header = self.llama_end_header
        self.max_new_tokens = 2048
        self.logger = logging.getLogger("ray.serve")
        self.logger.info(f"\n\n\n{self.local_model_type} LLM Engine is ready\n\n\n")

    def _template_header(self, role:str = "{role}") -> str:
        return f'{self.start_header}{role}{self.end_header}\n'

    def _model_processor(self, user_input, system_prompt):
        if "gemma" in self.local_model_type:
            return f'{system_prompt}\n{user_input}\n{self.end_header}\n{self.start_header}'.strip() + 'model\n'
        else:
            return f'{user_input}'.strip()

    def get_prompt(
        self,
        user_input: str, 
        chat_history: list[tuple[str, str]] =[],
        system_prompt: str = ""
    ) -> str:
        def template_dict(role, prompt):
            return { "role": role, ("content" if "gemma" in self.local_model_type else "prompt"): prompt }
        
        if any([model_name in self.local_model_type for model_name in ["gemma", ]]):
            prompt_texts = []
            if system_prompt != '' and "gemma" not in self.local_model_type:
                prompt_texts.append(template_dict(role="system", prompt=system_prompt))
            for history_role, history_response in chat_history:
                prompt_texts.append(template_dict(role=history_role, prompt=history_response.strip()))
            prompt_texts.append(template_dict(
                role="user",
                prompt=self._model_processor(user_input, system_prompt)))
            prompt_texts = self.tokenizer.apply_chat_template(prompt_texts, tokenize=False)
        else:
            prompt_texts = [f"{self.bos_token}"]
            chat_template = self._template_header() + '{prompt}' + self.eot_token +'\n'
            generate_template = chat_template + self._template_header(role="assistant")
            if system_prompt != '':
                prompt_texts.append(chat_template.format(role="system", prompt=system_prompt.strip()))
            for history_role, history_response in chat_history:
                prompt_texts.append(chat_template.format(role=history_role, prompt=history_response.strip()))
            prompt_texts.append(generate_template.format(role="user", prompt=user_input.strip()))

        return "".join(prompt_texts) if not isinstance(prompt_texts[0], dict) else prompt_texts


    def formatting(
        self, 
        prompt: List[str] | List[dict], 
        return_tensors: str = "pt"
    ) -> dict:
        if isinstance(prompt, list) and isinstance(prompt[0], dict):
            return [{
                "input_ids": self.tokenizer.apply_chat_template(p, return_tensors=return_tensors)
            } for p in prompt]
        elif isinstance(prompt, list) and isinstance(prompt[0], str):
            return self.tokenizer(prompt, return_tensors=return_tensors)
        elif isinstance(prompt, str):
            return self.tokenizer(prompt, return_tensors=return_tensors)
        else:
            # self.logger.info(prompt)
            return { 
                "input_ids": self.tokenizer.apply_chat_template(prompt, return_tensors=return_tensors)
            }

    def generate_config(
        self, 
        **kwargs
    ):
        generation_config = dict(
            do_sample=False,
            temperature=0.3,
            max_new_tokens=self.max_new_tokens,
            # penalty_alpha=0.5,
            # no_repeat_ngram_size=5,
            # frequency_penalty=0.0,
            # presence_penalty=0.0,
            top_p=0.99,
            use_cache=True)
        generation_config.update(kwargs)
        return generation_config

    def vllm_generate_config(
        self, 
        **kwargs
    ):
        from vllm.sampling_params import SamplingParams
        return SamplingParams(
            # repetition_penalty=1.0,
            # frequency_penalty=1.0,
            # presence_penalty=1.0,
            temperature=0.3,
            top_p=0.99,
            max_tokens=self.max_new_tokens)
    
    def _set_templat(
        self,
        input_text:str,
        input_prompt:str = None,
        input_history:List[str] = [],
        **kwargs
    ):
        # TODO: if need to process template, edit this code.
        return self.get_prompt(
            user_input=input_text,
            chat_history=input_history,
            system_prompt=input_prompt,
            **kwargs)
    
    @torch.inference_mode()
    def _generate(
        self, 
        prompt: str, 
    ):
        if torch.cuda.is_available(): # vllm generation
            output = self.model.generate(
                prompts=prompt,
                sampling_params=self.vllm_generate_config(), 
                use_tqdm=False)
            output_str = [out.outputs[0].text for out in output]
        else: # ipex, ov generation
            # self.logger.info(prompt)
            inputs = self.formatting(prompt=prompt)
            prefix_length = inputs["input_ids"].shape[-1]
            print(prefix_length)
            output = self.model.generate(**self.generate_config(**inputs))
            output_str = self.tokenizer.batch_decode(output, skip_special_tokens=True)[prefix_length:]
        return [out.replace(". ", ".\n") for out in output_str]

    @torch.inference_mode()
    def _make_generate(
        self,
        input_text: str,
        input_prompt: str = None,
        input_history: List[str] = [],
        **kwargs
    ) -> str:
        prompt = self._set_templat(
            input_text=input_text, 
            input_prompt=input_prompt, 
            input_history=input_history,
            **kwargs)
        return self._generate(prompt)[0]
 
    @torch.inference_mode()
    def _make_batch_generate(
        self,
        input_text: List[str],
        input_prompt: List[str] = None,
        input_history: List[List[str]] = [],
        **kwargs
    ) -> str:
        prompt = [
            self._set_templat(
                input_text=batch_input_text, 
                input_prompt=batch_input_prompt, 
                input_history=batch_input_history) 
            for batch_input_text, batch_input_prompt, batch_input_history in list(
                zip_longest(input_text, input_prompt, input_history, fillvalue=[]))]
        # print(prompt)
        return self._generate(prompt)

    @torch.inference_mode()
    def generate_stream(
        self, 
        input_text: str, 
        input_prompt: str = None,
        input_history: List = [],
        **kwargs
    ):
        input_text = self._set_templat(
            input_text=input_text,
            input_prompt=input_prompt,
            input_history=input_history,
            **kwargs)
        inputs = self.formatting(prompt=input_text.strip(), return_tensors="pt")
        inputs.update(dict(streamer=self.text_streamer))
        thread = Thread(
            target=self.model.generate, 
            kwargs=self.generate_config(**inputs))
        thread.start()
        for new_text in self.text_streamer:
            yield new_text

    @torch.inference_mode()
    def generate_stream_cuda(
        self, 
        input_text: str, 
        input_prompt: str = None,
        input_history: List = [],
        **kwargs
    ):
        # inputs = self.formatting(prompt=prompt , return_tensors="pt")
        response = self._make_generate(
            input_text=input_text, 
            input_prompt=input_prompt,
            input_history=input_history)
        for new_text in response:
            yield new_text

    @torch.inference_mode()
    def _raw_generate(
        self, 
        input_text: str, 
        input_prompt: str = None,
        input_history: List = [],
        max_length: int = 4096,
        **kwargs
    ):
        prompt = self._set_templat(
            input_text=input_text, 
            input_prompt=input_prompt, 
            input_history=input_history,
            **kwargs)
        input_ids = self.formatting(prompt=prompt, return_tensors="pt")["input_ids"]
        for _ in range(max_length):
            outputs = self.model(input_ids=input_ids)[0]
            next_token = torch.unsqueeze(torch.unsqueeze(torch.argmax(outputs[0, -1, :]), 0),1)
            if next_token == self.tokenizer.eos_token_id:
                break
            input_ids = torch.concatenate([input_ids, next_token], axis=-1)
            yield self.tokenizer.decode(next_token[0], skip_special_tokens=True)

    def _generation_wrapper(
        self, 
        stream: bool = False,
        batch: bool = False,
        **kwargs
    ):
        if torch.cuda.is_available() and stream:
            return self.generate_stream_cuda(**kwargs)
        elif batch:
            return self._make_batch_generate(**kwargs)
        elif stream:
            return self.generate_stream(**kwargs)
        else:
            return self._make_generate(**kwargs)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 3,
        "target_ongoing_requests": 5,
    },
    ray_actor_options=get_accelerator(),
    max_ongoing_requests=10)
class LLMService(GenerationService):
    '''
    Local LLM Service
    '''
    def summarize(
        self, 
        input_text: str|List[str], 
        language: str|List[str],
        prompt_type: str|List[str],
        input_prompt: str|List[str] = None, 
        stream: bool = False, 
        batch: bool = False
    ):
        if batch:
            default_system_prompt = [select_summary_domain(_t, _l) for _t, _l in zip(prompt_type, language)]
            input_prompt = [default_system_prompt[i] if p is None else p for i, p in enumerate(input_prompt)]
            input_history = [prompt.DEFAULT_SUMMARY_FEW_SHOT] * len(input_text)
        else:
            default_system_prompt = select_summary_domain(prompt_type, language)
            input_prompt = default_system_prompt if input_prompt is None else input_prompt
            input_history = prompt.DEFAULT_SUMMARY_FEW_SHOT
        
        return self._generation_wrapper(
            stream=stream, 
            batch=batch,
            **dict(
                input_text=input_text, 
                input_prompt=input_prompt,
                input_history=input_history))

    def translate(
        self, 
        input_text: str|List[str],
        source_language:str,
        detect_language:str,
        target_language:str,
        history: List[str]|List[List[str]],
        input_prompt: str|List[str] = None, 
        stream: bool = False, 
        batch: bool = False
    ): 
        default_few_shots: str = prompt.DEFAULT_TRANSLATION_FEW_SHOT
        default_system_prompt: str = prompt.DEFAULT_TRANSLATION_SYSTEM_PROMPT
        user_system_prompt = [default_system_prompt + default_few_shots] * len(input_text)        
        generation_prompt = [
            prompt.TRANSLATION_LANGUAGE_PROMPT.format(
                history="\n".join([f"    {_h}" for _h in h]),
                source=s,
                detect=d,
                target=t,
                context=" ".join([h[-1] if len(h)>0 else "", i]),
                input_text=i)
        for s,d,t,h,i in zip(source_language, detect_language, target_language, history, input_text)]
        if isinstance(input_text, list):
            input_text = [f"source language: {text}" for text in input_text]
        
        return self._generation_wrapper(
            stream=stream, batch=batch,
            **dict(
                input_text=generation_prompt, 
                input_prompt=user_system_prompt, 
                default_few_shots=default_few_shots, 
                default_system_prompt=user_system_prompt))

    def translate_summarize(
        self, 
        input_text: str|List[str], 
        source_language:str,
        detect_language:str,
        target_language:str,        
        history: List[str]|List[List[str]],
        input_prompt: str|List[str] = None, 
        stream: bool = False, 
        batch: bool = False
    ):
        default_few_shots: str = prompt.DEFAULT_TRANSLATION_FEW_SHOT
        default_system_prompt: str = [
            prompt.DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT.format(
                source=s,
                target=",".join(t) if len(t)>2 else t[0])
        for s,d,t,h in zip(source_language, detect_language, target_language, history)]
        
        user_system_prompt = [
            prompt.DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT.format(
                source=s,
                target=",".join(t) if len(t)>2 else t[0])
        for s,d,t,h in zip(source_language, detect_language, target_language, history)]

        return self._generation_wrapper(
            stream=stream, batch=batch,
            **dict(
                input_text=input_text, 
                input_prompt=user_system_prompt, 
                default_few_shots=default_few_shots, 
                default_system_prompt=default_system_prompt))
