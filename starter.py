import os
import argparse
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    set_global_service_context,
)
import dotenv
import logging
import sys
import os.path
from typing import Callable, Tuple, Any
from projectgurukul.readers import CSVReader, RamayanaCSVReader
dotenv.load_dotenv('.env')
from dataclasses import dataclass

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
    "ramayana": ScriptureInfo(name="Valmiki Ramayana", directory="ramayana", load_method=load_ramayana, metadatas_to_display = ('kanda','saraga')),
    "gita": ScriptureInfo(name="Bhagavad Gita", directory="gita", load_method=load_gita, metadatas_to_display=('chapter','verse')),
}


def setup_service_context(is_offline):
    if is_offline:
        print("Using offline local models.")

        # Avoids unnecessary logs in online mode
        from projectgurukul.custom_models import embedders, llms

        instructor_embeddings = embedders.InstructorEmbeddings(
            embed_batch_size=1)
        llm = llms.get_phi2_llm()  # llms.get_tinyllama_llm()
        service_context = ServiceContext.from_defaults(
            chunk_size=512, llm=llm, context_window=2048, embed_model=instructor_embeddings)
        set_global_service_context(service_context)
        storage_dir = '.storage_instructembed'
        similarity_top_k = 1
    else:
        print("Using openAI models")
        storage_dir = '.storage'
        similarity_top_k = 3

    return storage_dir, similarity_top_k

def get_query_engines(scripture, similarity_top_k, is_offline):
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
    return index.as_query_engine(similarity_top_k=similarity_top_k)


def main():
    parser = argparse.ArgumentParser(
        description='Process some questions about the Gita.')
    parser.add_argument('--question', metavar='question', type=str,
                        help='the question to process')
    parser.add_argument('--offline', action='store_true',
                        help='use local models')

    parser.add_argument('--debug', action='store_true',
                        help='print debug logs')

    parser.add_argument('--scripture', type=str, default='ramayana',
                        help='The scripture to fetch answers from (default: ramayana)',
                        choices=SCRIPTURE_MAPPING.keys())

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    scripture_info = SCRIPTURE_MAPPING[args.scripture]
    query_engine = get_query_engines(args.scripture,similarity_top_k=3,is_offline=args.offline)
    
    if len(sys.argv) < 3:
        print(
            "Usage: python main.py [--offline] 'Why Arjuna was confused?'")
        sys.exit(1)

    query = args.question
    print("Q:", query)

    response = query_engine.query(
        query + " Also, Mention the source, Sanskrit shlokas, and logic behind the answer. Properly format your answer using markdowns")
    print("A:", response)

    print(f"\n\nSources: {scripture_info.name}")
    for i, source in enumerate(response.source_nodes):
        print(f"\n\n[{i+1}]:" ,{k:v for k,v in source.node.metadata.items() if k in scripture_info.metadatas_to_display})
        print(source.node.get_content()[:500], '...')


if __name__ == "__main__":
    main()
