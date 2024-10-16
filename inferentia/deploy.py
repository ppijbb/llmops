from fastapi import FastAPI
from vllm import LLM, SamplingParams
from optimum.neuron import NeuronModelForCausalLM
import uvicorn

app = FastAPI(title="dialog summary")


def vllm():
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
        tensor_parallel_size=2)
    # Generate texts from the prompts. The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.
    outputs = llm.generate(prompts, sampling_params)
    # Print the outputs.
    result_text = ""
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
        result_text += generated_text
    return result_text

def main_f():
    # 컴파일을 위한 인자 설정
    compiler_args = {
        "num_cores": 2, 
        "auto_cast_type": 'bf16'
        }
    input_shapes = {
        "batch_size": 1, 
        "sequence_length": 128
        }

    # 사전학습한 모델을 불러오고 설정한 값에 따라 컴파일을 수행 요청
    model = NeuronModelForCausalLM.from_pretrained(
        model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        export=True,
        **compiler_args,
        **input_shapes
    )
    # 컴파일된 모델을 저장
    return model.config


@app.get("/")
def read_root():
    return {
        "message": "Neuron model is compiled and saved",
        "neuron_model": main_f(),
        "text": vllm()
        }

# uvicorn.run(app, host="0.0.0.0", port=8000)
