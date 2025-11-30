from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
DATA_PATH = "data/"
def load_pdf(data):
    loader= DirectoryLoader(
        data,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
        )
    documents = loader.load()
    return documents

docs = load_pdf(data=DATA_PATH)
print(f"Total number of documents: {len(docs)}")


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    split_docs = text_splitter.split_documents(documents)
    return split_docs

splitted_docs = split_documents(documents = docs)

print(f"Total number of splitted documents: {len(splitted_docs)}")

embeddings =HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    # return GoogleGenerativeAIEmbeddings()

# DB_FAISS_PATH = "vector_store/faiss_index"

DB_Chroma_PATH = "vector_store/chroma_index"
vector_store = Chroma.from_documents(splitted_docs, embedding=embeddings, persist_directory=DB_Chroma_PATH)
# vector_store.save_local(DB_Chroma_PATH)
vector_store.persist()
print(f"Chroma index saved at {DB_Chroma_PATH}")