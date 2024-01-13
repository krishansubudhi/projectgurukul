from llama_index.llms import HuggingFaceLLM, ChatMessage
from llama_index.prompts import PromptTemplate
import torch
import logging

def get_device_and_dtype():
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
        device = "mps"
        dtype = torch.float16
    else:
        device = "auto"
        dtype = "auto"
    return device, dtype

SYSTEM_PROMPT = "You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines."


def get_tinyllama_llm(context_window = 2048, max_new_tokens = 256):
    def messages_to_prompt(messages: ChatMessage):
        messages_dict = [
                    {"role": message.role.value, "content": message.content}
                    for message in messages
                ]
        prompt =  huggingllm._tokenizer.apply_chat_template(messages_dict, tokenize=False, add_generation_prompt=True)
        logging.debug(prompt)
        return prompt


    device, dtype = get_device_and_dtype()
    system_prompt = f"<|system|>"

    # This will wrap the default prompts that are internal to llama-index
    query_wrapper_prompt = PromptTemplate(
        system_prompt+"<|user|>{query_str}<|assistant|>")

    huggingllm = HuggingFaceLLM(
        context_window=context_window,
        is_chat_model=True,
        model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        tokenizer_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        max_new_tokens=max_new_tokens,
        stopping_ids=[2, 50256],
        generate_kwargs={'do_sample': False},
        model_kwargs={"torch_dtype": dtype},
        query_wrapper_prompt=query_wrapper_prompt,
        device_map = device
    )

    huggingllm.messages_to_prompt = messages_to_prompt
    return huggingllm



def get_phi2_llm(context_window = 2048, max_new_tokens = 256):

    role_maps = {
        "system" :"Instructions",
        "user" :"User Instructions"
    }
    def messages_to_prompt(messages: ChatMessage):
        prompt = ""
        for message in messages:
            role = message.role.value
            role = role_maps[role] if role in role_maps else role
            prompt += f"\n{role}:: {message.content}\n\n"
        prompt += "Response ::"
        logging.debug(prompt)
        return prompt
    device, dtype = get_device_and_dtype()

    # This will wrap the default prompts that are internal to llama-index
    query_wrapper_prompt = PromptTemplate("Instruct: {query_str}\nOutput: ")

    huggingllm = HuggingFaceLLM(
        context_window=context_window,
        is_chat_model=True,
        model_name="microsoft/phi-2",
        tokenizer_name="microsoft/phi-2",
        max_new_tokens=max_new_tokens,
        stopping_ids=[50256],
        generate_kwargs={'do_sample': False},
        model_kwargs={"torch_dtype": dtype, "trust_remote_code" :True},
        query_wrapper_prompt=query_wrapper_prompt,
        messages_to_prompt = messages_to_prompt,
        device_map = device
    )
    return huggingllm