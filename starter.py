from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
import dotenv
import logging
import sys
import os.path
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
import pandas as pd

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

dotenv.load_dotenv('.env')


class MyFileReader(BaseReader):
    def load_data(self, file, extra_info=None):
        df = pd.read_csv(file)
        documents = []
        for index, row in df.iterrows():
            # print(index, row.verse_number, extra_info)
            chapter, verse = row.verse_number.split(',')
            extra_info_row = {
                "verse": verse,
                "chapter": chapter
            }
            if extra_info:
                extra_info_row.update(extra_info)
            text = f'Sanskrit Shloka: {row.verse_in_sanskrit}\n\nEnglish Meaning: {
                row.meaning_in_english}'
            documents.append(Document(text=text + "Foobar",
                             extra_info=extra_info_row))
        return documents


BOOK_DIR = "./gita/"
# check if storage already exists
PERSIST_DIR = BOOK_DIR+".storage"
if not os.path.exists(PERSIST_DIR):
    # load the documents and create the index
    documents = SimpleDirectoryReader(
        input_dir=BOOK_DIR+"data", file_extractor={".csv": MyFileReader()}).load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# either way we can now query the index
query_engine = index.as_query_engine()

if len(sys.argv) <2:
    print("No question provided. \n python starter.py 'Why Arjuna was confused?'")

query = ' '.join(sys.argv[1:])
print("Q:" ,query)

response = query_engine.query(query + " Also, Mention the source, shlokas and logic behind the answer. Properly format your answer using markdowns")
print("A:", response)
