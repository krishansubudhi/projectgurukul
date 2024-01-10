from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.query_engine import CitationQueryEngine
import dotenv
import logging
import sys
import os.path
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
from projectgurukul.readers import CSVReader

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

dotenv.load_dotenv('.env')


def load_gita(directory):
    def preprocess(row):
        row['chapter'], row['verse'] = row.verse_number.split(', ')
        return row

    gita_reader = CSVReader(text_columns=['verse_in_sanskrit','translation_in_english','meaning_in_english'], metadata_columns=['chapter', 'verse'], preprocess = preprocess)
    documents = SimpleDirectoryReader(
        input_dir=directory, file_extractor={".csv": gita_reader}).load_data()
    return documents

def load_scripture_basics(directory):
    return SimpleDirectoryReader(input_dir=directory).load_data()

BOOK_DIR = "./data/gita/"


PERSIST_DIR = BOOK_DIR+".storage"
if not os.path.exists(PERSIST_DIR):
    documents = load_gita(BOOK_DIR+"data")
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# query_engine = index.as_query_engine()
query_engine = CitationQueryEngine.from_args(
    index,
    similarity_top_k=3,
    citation_chunk_size=512,
)

if len(sys.argv) <2:
    print("No question provided. \n python starter.py 'Why Arjuna was confused?'")

query = ' '.join(sys.argv[1:])
print("Q:" ,query)

response = query_engine.query(query + " Also, Mention the source, shlokas and logic behind the answer. Properly format your answer using markdowns")
print("A:", response)


print(len(response.source_nodes))
print(response.source_nodes[0].node.get_metadata_str())