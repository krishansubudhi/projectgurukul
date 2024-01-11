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
from projectgurukul.readers import CSVReader
dotenv.load_dotenv('.env')

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def load_gita(directory):
    def preprocess(row):
        row['chapter'], row['verse'] = row.verse_number.split(', ')
        return row

    gita_reader = CSVReader(text_columns=['verse_in_sanskrit', 'translation_in_english',
                            'meaning_in_english'], metadata_columns=['chapter', 'verse'], preprocess=preprocess)
    documents = SimpleDirectoryReader(
        input_dir=directory, file_extractor={".csv": gita_reader}).load_data()
    return documents


def load_scripture_basics(directory):
    return SimpleDirectoryReader(input_dir=directory).load_data()


def setup_service_context(args):
    if args.offline:
        print("Using offline local models.")

        # Avoids unnecessary logs in online mode
        from projectgurukul.custom_models import embedders, llms

        instructor_embeddings = embedders.InstructorEmbeddings(
            embed_batch_size=1)
        llm = llms.get_phi2_llm()
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


def main():
    parser = argparse.ArgumentParser(
        description='Process some questions about the Gita.')
    parser.add_argument('--question', metavar='question', type=str,
                        help='the question to process')
    parser.add_argument('--offline', action='store_true',
                        help='use local models')

    args = parser.parse_args()
    storage_dir, similarity_top_k = setup_service_context(args)

    BOOK_DIR = "./data/gita/"
    persist_dir = BOOK_DIR + storage_dir

    if not os.path.exists(persist_dir):
        documents = load_gita(BOOK_DIR + "data")
        print("Creating one-time document index ...")
        index = VectorStoreIndex.from_documents(documents)
        print("Finished creating document index.")
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        logging.info(f"loading from stored index {persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(similarity_top_k=similarity_top_k)

    if len(sys.argv) < 3:
        print(
            "Usage: python main.py [--offline] 'Why Arjuna was confused?'")
        sys.exit(1)

    query = args.question
    print("Q:", query)

    response = query_engine.query(
        query + " Also, Mention the source, Sanskrit shlokas, and logic behind the answer. Properly format your answer using markdowns")
    print("A:", response)

    print("\n\nSources:")
    for i, source in enumerate(response.source_nodes):
        print(f"\nSource [{i+1}]: ")
        print(source.node.metadata)

if __name__ == "__main__":
    main()
