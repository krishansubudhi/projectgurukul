import os
from llama_index import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    set_global_service_context,
    global_service_context,
    Response,
)
from llama_index.tools.query_engine import QueryEngineTool
from llama_index.query_engine.router_query_engine import RouterQueryEngine
from llama_index.retrievers import QueryFusionRetriever,BM25Retriever
from llama_index.query_engine import RetrieverQueryEngine
import dotenv
import logging
import os.path
from projectgurukul import scriptures
from projectgurukul import prompt_templates
dotenv.load_dotenv('.env')
from llama_index.llms import OpenAI
from llama_index.selectors.pydantic_selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)

SYSTEM_PROMPT = """You are answering texts on Hindu scriptures. Always make sure to follow these primary rules:
1. Be careful while answering and avoid hurting sentiments of people following hindu dharma. 
2. Always mention the source, Sanskrit shlokas, and logic behind the answer. 
3. Properly format your answer using markdowns.
"""

SCRIPTURE_MAPPING = {
    scriptures.Gita.ID : scriptures.Gita(),
    scriptures.Ramayana.ID : scriptures.Ramayana()
}

#Temporary. find a better way later.
def get_scripture_from_source_metadata(metadata: dict[str, str]) -> str:
    file_path = metadata['file_path']
    for _, scripture_info in SCRIPTURE_MAPPING.items():
        if f"/{scripture_info.DIRECTORY}/" in file_path:
            return scripture_info
    logging.error(f"No scripture could be inferred for file_path {file_path}.")
    return None

def setup_service_context(is_offline):
    if is_offline:
        print("Using offline local models.")

        # Avoids unnecessary logs in online mode
        from projectgurukul.custom_models import embedders, llms

        instructor_embeddings = embedders.InstructorEmbeddings(
            embed_batch_size=1)
        llm = llms.get_phi2_llm()  # llms.get_tinyllama_llm(system_prompt= SYSTEM_PROMPT)
        service_context = ServiceContext.from_defaults(
            chunk_size=512, llm=llm, context_window=2048, embed_model=instructor_embeddings)
        set_global_service_context(service_context)
        storage_dir = '.storage_instructembed'
        similarity_top_k = 1
    else:
        print("Using openAI models")
        llm = OpenAI(model="gpt-3.5-turbo-1106")#gpt-4-1106-preview
        service_context = ServiceContext.from_defaults(llm=llm)
        set_global_service_context(service_context)
        storage_dir = '.storage'
        similarity_top_k = 3

    return storage_dir, similarity_top_k

def get_query_engines(scripture, is_offline, data_dir = "data"):
    storage_dir, similarity_top_k = setup_service_context(is_offline)
    scripture_info = SCRIPTURE_MAPPING[scripture]
    BOOK_DIR = f"{data_dir}/{scripture_info.DIRECTORY}/"
    print(BOOK_DIR)
    persist_dir = BOOK_DIR + storage_dir

    if not os.path.exists(persist_dir):
        documents = scripture_info.load(BOOK_DIR + "data")
        print("Creating one-time document index ...")
        # TODO: Also add a KeywordStoreIndex
        # https://docs.llamaindex.ai/en/stable/examples/query_engine/RouterQueryEngine.html
        index = VectorStoreIndex.from_documents(documents)
        print("Finished creating document index.")
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        print(f"loading from stored index {persist_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(similarity_top_k=similarity_top_k)
    return query_engine

def get_router_query_engine(scriptures, is_offline, data_dir = "data"):
    query_engine_tools = []
    for scripture in scriptures:
        query_engine = get_query_engines(scripture, is_offline, data_dir)
        scripture_info = SCRIPTURE_MAPPING[scripture]
        tool = QueryEngineTool.from_defaults(query_engine, name=scripture_info.ID, description= scripture_info.DESCRIPTION)
        query_engine_tools.append(tool)
    print(query_engine_tools)
    router_query_engine =  RouterQueryEngine(
        selector=PydanticMultiSelector.from_defaults(),
        query_engine_tools=query_engine_tools,
    )
    return router_query_engine


def get_fusion_retriever(scriptures, is_offline, data_dir = "data"):
    retrievers = []
    storage_dir, similarity_top_k = setup_service_context(is_offline)
    for scripture in scriptures:
        scripture_info = SCRIPTURE_MAPPING[scripture]
        BOOK_DIR = f"{data_dir}/{scripture_info.DIRECTORY}/"
        persist_dir = BOOK_DIR + storage_dir

        index = load_index_from_storage(StorageContext.from_defaults(persist_dir=persist_dir))
        vector_retriever = index.as_retriever(similarity_top_k=similarity_top_k)
        # bm25_retriever = BM25Retriever.from_defaults(
        #     docstore=index.docstore, similarity_top_k=similarity_top_k
        # )
        retrievers.append(vector_retriever)


    retriever = QueryFusionRetriever(
        retrievers = retrievers,
        similarity_top_k=similarity_top_k,
        mode="simple", # TODO:Experiment with reciprocal rank
        num_queries=1,  # set this to 1 to disable query generation
        use_async=True,
        # query_gen_prompt="...",  # we could override the query generation prompt here
    )
    return retriever

def get_fusion_query_engine(scriptures, is_offline, data_dir = "data"):
    retriever = get_fusion_retriever(scriptures, is_offline, data_dir)
    query_engine = RetrieverQueryEngine.from_args(
    retriever,
    text_qa_template = prompt_templates.custom_text_qa_template)
    return query_engine

def get_empty_response():
    return Response("This is test response", [], {})