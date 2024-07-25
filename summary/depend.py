import os
import torch
from transformers import AutoTokenizer


def get_model(
    model_path: str = "/home/conan/workspace/kyi/play-llama/Meta-Llama-3-8B",
    adapter_path: str = "/home/conan/workspace/kyi/play-llama/expr/peft_Meta-Llama-3-8B_samsum_dataset"
    ):
        ## ---------------------------- ##
        # adapter_path = "expr/peft_Meta-Llama-3-8B_alpaca_dataset"

        # Load model in 4 bit,
        # which convert the relevant layers in the model into INT4 format
        if torch.cuda.is_available():
            from optimum.onnxruntime import ORTModelForCausalLM      
            from vllm import LLM

            model  = LLM(model = model_path)
        else:
            from ipex_llm.transformers import AutoModelForCausalLM
            from optimum.intel import OVModelForCausalLM

            model = OVModelForCausalLM.from_pretrained(model_path,
                                                       load_in_8bit=True,
                                                       cache_dir=os.getenv("HF_HOME"),
                                                       device="CPU",
                                                       use_cache=True,
                                                       compile=True,
                                                       ov_config={
                                                           "CPU_DENORMALS_OPTIMIZATION": "YES",
                                                           "INFERENCE_PRECISION_HINT": "INT8",
                                                           "CPU_SPARSE_WEIGHTS_DECOMPRESSION_RATE": "1.0",
                                                           "CACHE_DIR": os.getenv("HF_HOME"), 
                                                           "ALLOW_AUTO_BATCHING": "YES",
                                                           "PERF_COUNT": "YES"
                                                       })
        # -- adapter --
        if adapter_path is not None:
            model.load_adapter(adapter_path)
            
        model.eval()
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        return model, tokenizer
