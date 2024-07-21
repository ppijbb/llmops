import torch
import ray
import psutil
import numpy as np
from summary.depend import get_model

# ray.init(
#     num_cpus=psutil.cpu_count(logical=True), 
#     ignore_reinit_error=True,
#     )


def get_prompt(user_input: str, 
               chat_history: list[tuple[str, str]],
               system_prompt: str) -> str:
    prompt_texts = [f'<|begin_of_text|>']
    chat_template = '<|start_header_id|>{role}<|end_header_id|>\n\n{prompt}<|eot_id|>\n\n'
    generate_template = f'{chat_template}<|start_header_id|>assistant<|end_header_id|>\n\n'
    
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

    prompt_texts.append(generate_template.format(role="user", prompt=user_input.strip()))
    # prompt_texts.append(template_dict(role="user", prompt=history_input.strip()))

    return "".join(prompt_texts) if isinstance(prompt_texts[0], str) else prompt_texts


# @ray.remote
class LLMService(object):
    def __init__(self):
        self.model, self.tokenizer = get_model(
            # model_path="HuggingFaceH4/zephyr-7b-alpha", 
            model_path="OpenVINO/open_llama_3b_v2-int8-ov",
            adapter_path=None)
        
    def formatting(self, prompt: str):
        if isinstance(prompt, str):
            return self.tokenizer(prompt, return_tensors="pt")
        else:
            return self.tokenizer.apply_chat_template(prompt, return_tensors="pt")

    @torch.inference_mode()
    def _make_summary(self,
                      input_text: str) -> str:
        chat_template = {
            "user_input": input_text,
            "chat_history": [],
            "system_prompt": ""
        }
        prompt = get_prompt(**chat_template)
        inputs = self.formatting(prompt)
        output = self.model.generate(**inputs,
                                     use_cache=True,
                                     num_return_sequences=1,)
        output_str = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return output_str
    
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
