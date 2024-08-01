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

            # model = OVModelForCausalLM.from_pretrained(model_path,
            #                                            load_in_8bit=True,
            #                                            cache_dir=os.getenv("HF_HOME"),
            #                                            device="CPU",
            #                                            use_cache=True,
            #                                            compile=True,
            #                                            ov_config={
            #                                                "CPU_DENORMALS_OPTIMIZATION": "YES",
            #                                                "INFERENCE_PRECISION_HINT": "INT8",
            #                                                "CPU_SPARSE_WEIGHTS_DECOMPRESSION_RATE": "1.0",
            #                                                "CACHE_DIR": os.getenv("HF_HOME"), 
            #                                                "ALLOW_AUTO_BATCHING": "YES",
            #                                                "PERF_COUNT": "YES"
            #                                            })
            config = {
                   "architectures": [
                            "LlamaForCausalLM"
                        ],
                        "attention_bias": False,
                        "attention_dropout": 0.0,
                        "bos_token_id": 128000,
                        "eos_token_id": 128001,
                        "hidden_act": "silu",
                        "hidden_size": 4096,
                        "initializer_range": 0.02,
                        "intermediate_size": 14336,
                        "max_position_embeddings": 131072,
                        "mlp_bias": False,
                        "model_type": "llama",
                        "num_attention_heads": 32,
                        "num_hidden_layers": 32,
                        "num_key_value_heads": 8,
                        "pretraining_tp": 1,
                        "rms_norm_eps": 1e-05,
                        "rope_scaling": {
                            "factor": 8.0,
                            "low_freq_factor": 1.0,
                            "high_freq_factor": 4.0,
                            "original_max_position_embeddings": 8192,
                            "type": "llama3",
                            "rope_type": "llama3"
                        },
                        "rope_theta": 500000.0,
                        "tie_word_embeddings": False,
                        "torch_dtype": "bfloat16",
                        "transformers_version": "4.40.0",
                        "use_cache": True,
                        "vocab_size": 128256
                        }
            
            model = AutoModelForCausalLM.from_pretrained(model_path,
                                                         config=config,
                                                         load_in_8bit=True,
                                                         use_cache=True)
        # -- adapter --
        if adapter_path is not None:
            model.load_adapter(adapter_path)
            
        model.eval()
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        return model, tokenizer
