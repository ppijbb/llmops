import triton

print(triton.__version__)
from fastapi import FastAPI
from vllm import LLM, SamplingParams
from optimum.neuron import NeuronModelForCausalLM
from transformers import AutoTokenizer
import uvicorn
import os
import time

os.environ['NEURON_VISIBLE_CORES']='2'
os.environ['NEURON_RT_NUM_CORES']='2'


app = FastAPI(title="dialog summary")


def vllm():
    import vllm
    print("Call VLLM Function")
    print(vllm.__version__)
    # Sample prompts.
    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ]
    # Create a sampling params object.
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    # Create an LLM.
    llm = LLM(
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        max_num_seqs=8,
        # The max_model_len and block_size arguments are required to be same as max sequence length,
        # when targeting neuron device. Currently, this is a known limitation in continuous batching
        # support in transformers-neuronx.
        max_model_len=128,
        block_size=128,
        # The device can be automatically detected when AWS Neuron SDK is installed.
        # The device argument can be either unspecified for automated detection, or explicitly assigned.
        device="neuron",
        tensor_parallel_size=1)
    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    outputs = llm.generate(prompts, sampling_params)
    # Print the outputs.
    result_text = "안녕하세요 저는 미국에서온 "
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        result_text += generated_text
    return result_text

def main_f():
    print("Call Main Function")
    # 컴파일을 위한 인자 설정
    compiler_args = {
        "num_cores": 2, 
        "auto_cast_type": 'bf16'
        }
    input_shapes = {
        "batch_size": 1, 
        "sequence_length": 128
        }
    model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    # 사전학습한 모델을 불러오고 설정한 값에 따라 컴파일을 수행 요청
    model = NeuronModelForCausalLM.from_pretrained(
        model_id=model_path,
        export=True,
        # dynamic_batch_size=True,
        **compiler_args,
        **input_shapes)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, 
        trust_remote_code=True)

    # 컴파일된 모델을 저장
    start = time.time()
    result = model.generate(
        **tokenizer("Hello, my name is", return_tensors='pt'), 
        max_new_tokens=512,
        do_sample=True,
        temperature=0.9,
        top_k=50,
        top_p=0.9)
    print(tokenizer.decode(result[0]))
    print(time.time() - start)
    return model.config.to_dict()

@app.on_event("startup")
async def startup_event():
    main_f()
    # vllm()


@app.get("/")
def read_root():
    print("MAIN CALLED")
    return {
        "message": "Neuron model is compiled and saved",
        # "neuron_model": main_f(),
        "text": vllm()
        }

# uvicorn.run(app, host="0.0.0.0", port=8000)
