"""Load CV, split into chunks, embed, and store in ChromaDB."""
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings


def load_cv_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        result = file.read()
        return result


def chunk_cv(text: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    return splitter.create_documents([text])


def get_vector_store() -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_persist_dir),
    )


def build_cv_index() -> None:
    text = load_cv_text(settings.cv_path)
    chunks = chunk_cv(text)
    vector_store = get_vector_store()

    vector_store.delete_collection()
    vector_store = get_vector_store()

    ids = [f"cv-chunk-{i}" for i in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=ids)
    print(f"Indexed {len(chunks)} chunks into {settings.chroma_persist_dir}")


if __name__ == "__main__":
    build_cv_index()