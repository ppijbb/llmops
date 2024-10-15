from fastapi import FastAPI
import uvicorn

app = FastAPI(title="dialog summary")


def main_f():
    from optimum.neuron import NeuronModelForCausalLM


    # 컴파일을 위한 인자 설정
    compiler_args = {"num_cores": 2, "auto_cast_type": 'bf16'}
    input_shapes = {"batch_size": 1, "sequence_length": 4096}

    # 사전학습한 모델을 불러오고 설정한 값에 따라 컴파일을 수행 요청
    model = NeuronModelForCausalLM.from_pretrained(
        model_id="Gunulhona/Gemma-Ko-Merge",
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
        "neuron_model": main_f()
        }

uvicorn.run(app, host="0.0.0.0", port=8000)
