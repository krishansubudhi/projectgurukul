from InstructorEmbedding import INSTRUCTOR
from typing import Any, List
from InstructorEmbedding import INSTRUCTOR
from llama_index.embeddings.base import BaseEmbedding

from llama_index.bridge.pydantic import PrivateAttr
from llama_index.embeddings.base import BaseEmbedding
from angle_emb import AnglE, Prompts


class InstructorEmbeddings(BaseEmbedding):
    _model: INSTRUCTOR = PrivateAttr()
    _instruction: str = PrivateAttr()
    _instruction_query: str = PrivateAttr()
    def __init__(
        self, 
        instructor_model_name: str = "hkunlp/instructor-large",
        instruction: str = "Represent the Hindu Spiritual text for retrieval:",
        instruction_query: str = "Represent the hindu spiritual question for retrieving supporting documents:",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = INSTRUCTOR(instructor_model_name)
        self._instruction = instruction
        self._instruction_query = instruction_query

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._model.encode([[self._instruction_query, query]])
        return embeddings[0].tolist()
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._model.encode([[self._instruction, text]])
        return embeddings[0].tolist() 
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode([[self._instruction, text] for text in texts])
        return embeddings.tolist()


class AngleUAEEmbeddings(BaseEmbedding):
    _model: AnglE= PrivateAttr()

    def __init__(
        self, 
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = AnglE.from_pretrained('WhereIsAI/UAE-Large-V1', pooling_strategy='cls').cuda()
        self._model.set_prompt(prompt=Prompts.C)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._model.encode({'text': query}, to_numpy=True)
        return embeddings[0].tolist()
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._model.encode({'text': text})
        return embeddings[0].tolist() 
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode([{'text': text} for text in texts])
        return embeddings.tolist()
