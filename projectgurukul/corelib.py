import os
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    set_global_service_context,
    Response
)
import dotenv
import logging
import os.path
from typing import Callable, Tuple, Any
from projectgurukul.readers import CSVReader, RamayanaCSVReader
dotenv.load_dotenv('.env')
from llama_index.llms import OpenAI
from dataclasses import dataclass

SYSTEM_PROMPT = """You are answering texts on Hindu scriptures. Always make sure to follow these primary rules:
1. Be careful while answering and avoid hurting sentiments of people following hindu dharma. 
2. Always mention the source, Sanskrit shlokas, and logic behind the answer. 
3. Properly format your answer using markdowns.
"""



@dataclass
class ScriptureInfo:
    name: str
    directory: str
    load_method: Callable[[str], Tuple[str]]
    metadatas_to_display: Tuple[str]

def load_gita(directory):
    def preprocess(row):
        row['chapter'], row['verse'] = row.verse_number.split(', ')
        return row

    reader = CSVReader(text_columns=['verse_in_sanskrit', 'translation_in_english',
                                     'meaning_in_english'], metadata_columns=['chapter', 'verse'], preprocess=preprocess)
    documents = SimpleDirectoryReader(
        input_dir=directory, file_extractor={".csv": reader}).load_data()
    return documents


def load_ramayana(directory):
    reader = RamayanaCSVReader()
    documents = SimpleDirectoryReader(
        input_dir=directory, file_extractor={".csv": reader}).load_data()
    for document in documents:
        document.metadata["kanda"] = document.metadata["file_name"].split('.')[
            0].replace("kanda", " kanda")
    return documents


def load_scripture_basics(directory):
    return SimpleDirectoryReader(input_dir=directory).load_data()


SCRIPTURE_MAPPING = {
    "ramayana": ScriptureInfo(name="Valmiki Ramayana", directory="ramayana", load_method=load_ramayana, metadatas_to_display = ('kanda','sarga')),
    "gita": ScriptureInfo(name="Bhagavad Gita", directory="gita", load_method=load_gita, metadatas_to_display=('chapter','verse')),
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
    BOOK_DIR = f"./data/{scripture_info.directory}/"
    persist_dir = BOOK_DIR + storage_dir

    if not os.path.exists(persist_dir):
        documents = scripture_info.load_method(BOOK_DIR + "data")
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
    print("prompts_dict", prompts_dict)
    return query_engine
