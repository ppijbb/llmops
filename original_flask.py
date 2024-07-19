#import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
#import torch 
#GPU_NUM = 0
#device = torch.device(f'cuda:{GPU_NUM}')
#torch.cuda.set_device(device)

import torch
import time
import argparse

from ipex_llm.transformers import AutoModelForCausalLM
from transformers import AutoTokenizer

import traceback

## ---------------------------- ##
model_name = "/home/conan/workspace/kyi/play-llama/Meta-Llama-3-8B"
model_path = model_name

#adapter_name = "expr/peft_Meta-Llama-3-8B_alpaca_dataset"
adapter_name = "/home/conan/workspace/kyi/play-llama/expr/peft_Meta-Llama-3-8B_samsum_dataset"

# Load model in 4 bit,
# which convert the relevant layers in the model into INT4 format
model = AutoModelForCausalLM.from_pretrained(model_path,
                                             load_in_4bit=True,
                                             optimize_model=True,
                                             trust_remote_code=True,
                                             use_cache=True)

# -- adapter --
model.load_adapter(adapter_name)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# here the terminators refer to https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct#transformers-automodelforcausallm
terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>"),
    ]


input_text = """
6하원칙이란 어떤 주제에 대해 설명할 때, {누가, 언제, 어디서, 무엇을, 어떻게, 왜} 라는 6개 항목에 맞추어 설명하는 것을 말해. 
아래 대화 내용의 세부 사항을 6하원칙에 따라 요약해줘:
영희: 안녕 철수야, 내일 오후에 바쁘니?
철수: 바쁠것 같아.. 왜?
영희: 내일 동물 보호소에 같이 갈래? 
철수: 뭐 하려고?
영희: 아들한테 강아지 선물 하려고. 
철수: 좋은 생각이다. 그래 같이 가자. 
영희: 난 작은 강아지 한마리를 아들에게 사 줄까 해. 
철수: 그래 너무 크지 않은 녀석이 좋겠다.
---
요약:
"""

## ---------------------------- ##


# you could tune the prompt based on your own model,
# here the prompt tuning refers to https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3
DEFAULT_SYSTEM_PROMPT = """\
"""
n_predict = 32

def get_prompt(user_input: str, chat_history: list[tuple[str, str]],
               system_prompt: str) -> str:
    prompt_texts = [f'<|begin_of_text|>']

    if system_prompt != '':
        prompt_texts.append(f'<|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>')

    for history_input, history_response in chat_history:
        prompt_texts.append(f'<|start_header_id|>user<|end_header_id|>\n\n{history_input.strip()}<|eot_id|>')
        prompt_texts.append(f'<|start_header_id|>assistant<|end_header_id|>\n\n{history_response.strip()}<|eot_id|>')

    prompt_texts.append(f'<|start_header_id|>user<|end_header_id|>\n\n{user_input.strip()}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n')
    return ''.join(prompt_texts)

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Predict Tokens using `generate()` API for Llama3 model')
#     parser.add_argument('--repo-id-or-model-path', type=str, default="meta-llama/Meta-Llama-3-8B-Instruct",
#                       help='The huggingface repo id for the Llama3 (e.g. `meta-llama/Meta-Llama-3-8B-Instruct`) to be downloaded'
#                            ', or the path to the huggingface checkpoint folder')
#     parser.add_argument('--prompt', type=str, default="What is AI?",
#                        help='Prompt to infer')
#     parser.add_argument('--n-predict', type=int, default=32,
#                        help='Max tokens to predict')
#     args = parser.parse_args()

from flask import Flask, request, json, jsonify
app = Flask(__name__)

def format_llm_output(rlt_text):
    response = {
        'text': rlt_text
    }
    return jsonify(response)

@app.route("/summarize", methods=['POST'])
def summarize():    
    params = request.get_json()
    print(f"param: {params:} ")
    input_text = params["text"]
    # Generate predicted tokens
    try:
        with torch.inference_mode():
            #prompt = get_prompt(input_text, [], system_prompt=DEFAULT_SYSTEM_PROMPT)
            # ----------------------------------- #
            st = time.time()
            inputs = tokenizer(input_text, return_tensors="pt")
            output = model.generate(
                input_ids=inputs['input_ids'], 
                attention_mask=inputs['attention_mask'],
                use_cache=False, 
                num_return_sequences=1)
                                    
            end = time.time()
            output_str = tokenizer.decode(output[0], skip_special_tokens=False)
            #output_str = "hello from kyi"
            # ----------------------------------- #
            print(f'Inference time: {end-st} s')
            print('-'*20, 'Prompt', '-'*20)
            print(input_text)
            print('-'*20, 'Output (skip_special_tokens=False)', '-'*20)
            print(output_str)
            return format_llm_output(output_str)
    except Exception as e:
        print(traceback(e))
        return format_llm_output("Error in summarize")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10050)