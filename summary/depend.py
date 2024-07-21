import os
from ipex_llm.transformers import AutoModelForCausalLM
from optimum.intel import OVModelForCausalLM
from optimum.onnxruntime import ORTModelForCausalLM
from transformers import AutoTokenizer


def get_model(
    model_path: str = "/home/conan/workspace/kyi/play-llama/Meta-Llama-3-8B",
    adapter_path: str = "/home/conan/workspace/kyi/play-llama/expr/peft_Meta-Llama-3-8B_samsum_dataset"
    ):
        ## ---------------------------- ##
        # adapter_path = "expr/peft_Meta-Llama-3-8B_alpaca_dataset"

        # Load model in 4 bit,
        # which convert the relevant layers in the model into INT4 format
        model = AutoModelForCausalLM.from_pretrained(model_path,
                                                     load_in_4bit=True,
                                                     optimize_model=True,
                                                     trust_remote_code=True,
                                                     use_cache=True)
        # model = OVModelForCausalLM.from_pretrained(model_path,
        #                                            load_in_4bit=True,
        #                                            cache_dir=os.getenv("HF_HOME"),
        #                                            device="CPU",
        #                                            use_cache=True,
        #                                            compile=True,
        #                                            ov_config={
        #                                             "INFERENCE_PRECISION_HINT": "FP16",
        #                                             "PERF_COUNT": "YES"
        #                                            })
        # -- adapter --
        if adapter_path is not None:
            model.load_adapter(adapter_path)
            
        model.eval()
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        return model, tokenizer
