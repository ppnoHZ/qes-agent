from xml.dom.minidom import Document

# from langchain_milvus.vectorstores.milvus import Milvus
from langchain_milvus import Milvus

from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass


class MilvusVectorStore(BaseEmbedding):
    vector_store = None
    embedding = None
    uri = None

    def __init__(self, embedding, uri):
        self.embedding = embedding
        self.uri = uri
        self.vector_store = Milvus(
            embedding_function=embedding,
            connection_args={"uri": uri},
        )

    def embed(self, text: str):
        print("embed")

    def from_documents(self, documents: list[Document]):
        self.vector_store = Milvus(
            embedding_function=self.embedding,
            connection_args={"uri": self.uri},
        )
