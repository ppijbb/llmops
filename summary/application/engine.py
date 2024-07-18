import torch
import ray
import psutil

from summary.depend import get_model

num_cpus = psutil.cpu_count(logical=False)
ray.init(num_cpus=num_cpus, ignore_reinit_error=True)


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


@ray.remote
class LLMService(object):
    def __init__(self):
        self.model, self.tokenizer = get_model()
        self.model.eval()
    
    @torch.inference_mode()
    def _make_summary(self,
                      input_text: str, 
                      model, 
                      tokenizer) -> str:
        chat_template = {
            "user_input": input_text,
            "chat_history": [],
            "system_prompt": "You are summary llama"
        }
        prompt = get_prompt(**chat_template)
        inputs = self.tokenizer(prompt, return_tensors="pt") if isinstance(prompt, str) else tokenizer.apply_chat_template(prompt, return_tensors="pt")
        output = self.model.generate(**inputs, use_cache=False,)
        output_str = self.tokenizer.decode(output[0], skip_special_tokens=False)
        return output_str
    
    def summarize(self, input_text: str) -> str:
        return self._make_summary(input_text, self.model, self.tokenizer)


async def get_llm_service():
    yield LLMService.remote()
