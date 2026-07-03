"""Load CV, split into chunks, embed, and store in ChromaDB."""
import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings

logger = logging.getLogger(__name__)


def load_cv_text(path: Path) -> str:
    """Read and return the CV file contents as a string."""
    with open(path, "r", encoding="utf-8") as file:
        result = file.read()
        return result


def chunk_cv(text: str) -> list[Document]:
    """Split CV text into overlapping chunks suitable for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    return splitter.create_documents([text])


def get_vector_store() -> Chroma:
    """Initialize and return a Chroma vector store backed by HuggingFace sentence embeddings."""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_persist_dir),
    )


def build_cv_index() -> None:
    """Load the CV, clear any existing index, and re-index all chunks into ChromaDB."""
    text = load_cv_text(settings.cv_path)
    chunks = chunk_cv(text)
    vector_store = get_vector_store()

    logger.debug("Clearing existing CV index at %s", settings.chroma_persist_dir)
    vector_store.delete_collection()
    vector_store = get_vector_store()

    ids = [f"cv-chunk-{i}" for i in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=ids)
    logger.info("Indexed %d chunks into %s", len(chunks), settings.chroma_persist_dir)


if __name__ == "__main__":
    build_cv_index()