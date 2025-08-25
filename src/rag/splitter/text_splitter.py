from langchain_text_splitters import RecursiveCharacterTextSplitter


def text_splitter(docs):

    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    chunks = text_splitter.split_documents(docs_list)
    return chunks