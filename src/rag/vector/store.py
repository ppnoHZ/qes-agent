from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.utils import print_text


from qes_embedding.utils.milvus import MilvusVectorStore

embedding = OpenAIEmbeddings(
    model="BAAI/bge-large-zh-v1.5",
    api_key="sk-zdtfnwbgomtpuuhmduuiqeeivsbyunepxatgyurhjbcdlrhm",
    base_url="https://api.siliconflow.cn/v1",
)
milvus_uri = "./db/milvus.db"

milvus_embedding = MilvusVectorStore(embedding=embedding, uri=milvus_uri)


class VectorStore:
    name = None

    def __init__(self, doc_splits: list[Document], name=None, description=None):
        self.name = name
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=doc_splits,
            embedding=OpenAIEmbeddings(
                model="BAAI/bge-large-zh-v1.5",
                api_key="sk-zdtfnwbgomtpuuhmduuiqeeivsbyunepxatgyurhjbcdlrhm",
                base_url="https://api.siliconflow.cn/v1",
            ),
        )
        self.retriever_tool = create_retriever_tool(
            self.vectorstore.as_retriever(),
            name,
            description,
        )

    def from_documents(cls, documents: list[Document]):
        embeddings = OpenAIEmbeddings(
            model="BAAI/bge-large-zh-v1.5",
            api_key="sk-zdtfnwbgomtpuuhmduuiqeeivsbyunepxatgyurhjbcdlrhm",
            base_url="https://api.siliconflow.cn/v1",
        )
        return cls(documents, embedding=embeddings)

    def retrieve(self, query):
        print(query)
        return self.vectorstore.similarity_search(query)


if __name__ == "__main__":
    print_text("Vector Store", "red")
    doc = Document(
        page_content="QES is lenovo quality ecosystem",
        metadata={"source": "https://leqes.lenovo.com"},
    )
    vector_store = VectorStore(
        [doc],
        name="QES",
        description="qes ecosystem",
    )
    query = "What is the QES?"
    results = vector_store.retrieve(query)
    print(results)
