from __future__ import annotations

from pathlib import Path
from typing import Sequence

from langchain_core.documents import Document 
from langchain_community.vectorstores import FAISS

from app.retrieval.embeddings import get_embedding_model


class FAISSVectorStore:
    """
    Wrapper around FAISS.

    Responsibilities:
        - build index
        - save index
        - load index
        - expose the underlying vector store
    """

    def __init__(
        self,
        persist_directory: Path,
    ) -> None:

        self.persist_directory = Path(
            persist_directory
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            self.persist_directory
        )

        self.vectorstore: FAISS | None = None

    def build(
        self,
        documents: Sequence[Document],
    ) -> FAISS:
        """
        Build a new FAISS index from documents.
        """

        if not documents:
            raise ValueError(
                "Cannot build vector store from empty documents."
            )

        embeddings = get_embedding_model()

        self.vectorstore = (
            FAISS.from_documents(
                documents=documents,
                embedding=embeddings,
            )
        )

        return self.vectorstore

    def save(self) -> None:
        """
        Persist FAISS index to disk.
        """

        if self.vectorstore is None:
            raise RuntimeError(
                "Vector store has not been built."
            )

        self.vectorstore.save_local(
            str(self.index_path)
        )

    def load(self) -> FAISS:
        """
        Load an existing FAISS index from disk.
        """

        embeddings = get_embedding_model()

        self.vectorstore = (
            FAISS.load_local(
                str(self.index_path),
                embeddings,
                allow_dangerous_deserialization=True,
            )
        )

        return self.vectorstore

    def get(self) -> FAISS:
        """
        Return the currently loaded vector store.
        """

        if self.vectorstore is None:
            raise RuntimeError(
                "Vector store is not loaded."
            )

        return self.vectorstore

    def exists(self) -> bool:
        """
        Check whether a persisted FAISS index exists.
        """

        index_file = (
            self.index_path / "index.faiss"
        )

        metadata_file = (
            self.index_path / "index.pkl"
        )

        return (
            index_file.exists()
            and metadata_file.exists()
        )