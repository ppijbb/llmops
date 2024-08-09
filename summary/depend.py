import os
import torch
from transformers import AutoTokenizer


def get_model(
    model_path: str = "/home/conan/workspace/kyi/play-llama/Meta-Llama-3-8B",
    adapter_path: str = "/home/conan/workspace/kyi/play-llama/expr/peft_Meta-Llama-3-8B_samsum_dataset",
    inference_tool: str = "ipex",
    ):
        ## ---------------------------- ##
        # adapter_path = "expr/peft_Meta-Llama-3-8B_alpaca_dataset"

        # Load model in 4 bit,
        # which convert the relevant layers in the model into INT4 format
        if torch.cuda.is_available():
            from optimum.onnxruntime import ORTModelForCausalLM      
            from vllm import LLM

            model  = LLM(
                model = model_path,
                # quantization="fp8",
                trust_remote_code=True,
                gpu_memory_utilization=0.8,
            )

        else:
            from ipex_llm.transformers import AutoModelForCausalLM
            from optimum.intel import OVModelForCausalLM
            import openvino as ov


            if inference_tool == "ipex":
                model = AutoModelForCausalLM.from_pretrained(model_path,
                                                             load_in_4bit=True,
                                                             optimize_model=True,
                                                             trust_remote_code=True,
                                                             use_cache=True)
                model.eval()
            else:
                model = OVModelForCausalLM.from_pretrained(
                    model_path,
                    load_in_8bit=True,
                    cache_dir=os.getenv("HF_HOME"),
                    device="CPU",
                    use_cache=True,
                    compile=True,
                    ov_config={
                        ov.properties.streams.num : ov.properties.streams.Num.NUMA,
                        ov.properties.hint.num_requests: 1,
                        ov.properties.hint.execution_mode: ov.properties.hint.ExecutionMode.ACCURACY,
                        # ov.properties.hint.performance_mode: ov.properties.hint.PerformanceMode.LATENCY,
                        ov.properties.hint.performance_mode: ov.properties.hint.PerformanceMode.THROUGHPUT,
                        ov.properties.hint.inference_precision: ov.Type.bf16,
                        ov.properties.intel_cpu.denormals_optimization: True,
                        ov.properties.inference_num_threads: 8,
                        ov.properties.hint.enable_hyper_threading : True,
                        ov.properties.hint.enable_cpu_pinning: True,
                        ov.properties.hint.allow_auto_batching: True,
                        ov.properties.cache_dir: os.getenv("HF_HOME"), 
                        # ov.properties.available_devices: "CPU",
                        # ov.properties.loaded_from_cache: True,
                        # ov.properties.intel_cpu.sparce_weights_decompression_rate: 1.0,
                    })
                model.eval()

        # -- adapter --
        if adapter_path is not None:
            model.load_adapter(adapter_path)
            
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        return model, tokenizer
