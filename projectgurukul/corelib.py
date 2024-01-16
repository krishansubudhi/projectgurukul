import os
from llama_index import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    set_global_service_context,
    Response,
)
import dotenv
import logging
import os.path
from typing import Callable, Tuple, Any
from projectgurukul import scriptures
dotenv.load_dotenv('.env')
from llama_index.llms import OpenAI
from dataclasses import dataclass

SYSTEM_PROMPT = """You are answering texts on Hindu scriptures. Always make sure to follow these primary rules:
1. Be careful while answering and avoid hurting sentiments of people following hindu dharma. 
2. Always mention the source, Sanskrit shlokas, and logic behind the answer. 
3. Properly format your answer using markdowns.
"""

SCRIPTURE_MAPPING = {
    scriptures.Gita.ID : scriptures.Gita(),
    scriptures.Ramayana.ID : scriptures.Ramayana()
}


def setup_service_context(is_offline):
    if is_offline:
        print("Using offline local models.")

        # Avoids unnecessary logs in online mode
        from projectgurukul.custom_models import embedders, llms

        instructor_embeddings = embedders.InstructorEmbeddings(
            embed_batch_size=1)
        llm = llms.get_phi2_llm(system_prompt= SYSTEM_PROMPT)  # llms.get_tinyllama_llm(system_prompt= SYSTEM_PROMPT)
        service_context = ServiceContext.from_defaults(
            chunk_size=512, llm=llm, context_window=2048, embed_model=instructor_embeddings)
        set_global_service_context(service_context)
        storage_dir = '.storage_instructembed'
        similarity_top_k = 1
    else:
        print("Using openAI models")
        llm = OpenAI(model="gpt-3.5-turbo", system_prompt=SYSTEM_PROMPT)#gpt-4-1106-preview
        service_context = ServiceContext.from_defaults(llm=llm)
        set_global_service_context(service_context)
        storage_dir = '.storage'
        similarity_top_k = 3

    return storage_dir, similarity_top_k

def get_query_engines(scripture, is_offline):
    storage_dir, similarity_top_k = setup_service_context(is_offline)
    scripture_info = SCRIPTURE_MAPPING[scripture]
    BOOK_DIR = f"./data/{scripture_info.DIRECTORY}/"
    persist_dir = BOOK_DIR + storage_dir

    if not os.path.exists(persist_dir):
        documents = scripture_info.load(BOOK_DIR + "data")
        print("Creating one-time document index ...")
        index = VectorStoreIndex.from_documents(documents)
        print("Finished creating document index.")
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        logging.info(f"loading from stored index {persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(similarity_top_k=similarity_top_k)
    prompts_dict = query_engine.get_prompts()
    return query_engine

def get_empty_response():
    return Response("This is test response", [], {})