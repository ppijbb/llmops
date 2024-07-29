from optimum.neuronx import NeuronModelForCausalLM


# 컴파일을 위한 인자 설정
compiler_args = {"num_cores": 2, "auto_cast_type": 'bf16'}
input_shapes = {"batch_size": 1, "sequence_length": 4096}

# 사전학습한 모델을 불러오고 설정한 값에 따라 컴파일을 수행 요청
model = NeuronModelForCausalLM.from_pretrained(
    model_id="finetuned-model-name-or-path",
    export=True,
    **compiler_args,
    **input_shapes
)
# 컴파일된 모델을 저장
model.save_pretrained("compiled-model-name-or-path")