from llama_index.llms import HuggingFaceLLM
from llama_index.prompts import PromptTemplate
import torch


def get_tinyllama_llm():
    system_prompt = """<|system|> You are an helpful agent who can answer users question.
    """

    # This will wrap the default prompts that are internal to llama-index
    query_wrapper_prompt = PromptTemplate(
        system_prompt+"<|user|>{query_str}<|assistant|>")

    huggingllm = HuggingFaceLLM(
        context_window=2048,
        is_chat_model=True,
        model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        # model=model,
        tokenizer_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        max_new_tokens=64,
        stopping_ids=[2],
        generate_kwargs={"temperature": 0.01, 'do_sample': True},
        model_kwargs={"torch_dtype": torch.float16},
        query_wrapper_prompt=query_wrapper_prompt,
    )

    huggingllm.messages_to_prompt = lambda messages: huggingllm._tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    return huggingllm
