from __future__ import annotations

import re
from typing import Iterable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class KnowledgeBaseChunker:
    """
    Chunk AcmeCloud knowledge-base documents while preserving useful
    metadata and, where possible, Markdown section boundaries.

    Strategy:
        1. Split documents into Markdown sections.
        2. Split oversized sections using RecursiveCharacterTextSplitter.
        3. Attach section metadata to every resulting chunk.
        4. Generate deterministic chunk IDs.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 75,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
            length_function=len,
        )

    def chunk(
        self,
        documents: Iterable[Document],
    ) -> list[Document]:
        """
        Convert loaded documents into retrieval chunks.
        """

        chunks: list[Document] = []

        for document in documents:
            section_chunks = self._chunk_document(document)
            chunks.extend(section_chunks)

        self._assign_chunk_ids(chunks)

        return chunks

    def _chunk_document(
        self,
        document: Document,
    ) -> list[Document]:
        """
        Split a document into Markdown-aware sections first.
        """

        sections = self._split_markdown_sections(
            document.page_content
        )

        output: list[Document] = []

        for section_index, section in enumerate(
            sections
        ):
            heading = section["heading"]
            content = section["content"]

            if not content.strip():
                continue

            # Add heading into the text so the embedding model
            # knows the semantic context of the section.
            section_text = self._build_section_text(
                heading=heading,
                content=content,
            )

            # Small enough section: keep it intact.
            if len(section_text) <= self.chunk_size:
                pieces = [section_text]

            # Large section: recursively split.
            else:
                pieces = self.text_splitter.split_text(
                    section_text
                )

            for piece_index, piece in enumerate(pieces):
                metadata = dict(document.metadata)

                metadata.update(
                    {
                        "section": heading,
                        "section_index": section_index,
                        "piece_index": piece_index,
                    }
                )

                output.append(
                    Document(
                        page_content=piece.strip(),
                        metadata=metadata,
                    )
                )

        return output

    @staticmethod
    def _split_markdown_sections(
        text: str,
    ) -> list[dict[str, str]]:
        """
        Split Markdown content at heading boundaries.

        Supports:
            # Heading
            ## Heading
            ### Heading

        Front-matter at the beginning of our documents is treated
        as part of the document preamble rather than a section.
        """

        lines = text.splitlines()

        sections: list[dict[str, str]] = []

        current_heading = "document_preamble"
        current_content: list[str] = []

        for line in lines:
            heading_match = re.match(
                r"^(#{1,6})\s+(.*)$",
                line.strip(),
            )

            if heading_match:
                # Save previous section
                previous_content = "\n".join(
                    current_content
                ).strip()

                if previous_content:
                    sections.append(
                        {
                            "heading": current_heading,
                            "content": previous_content,
                        }
                    )

                current_heading = (
                    heading_match.group(2).strip()
                )

                current_content = []

            else:
                current_content.append(line)

        # Save final section
        final_content = "\n".join(
            current_content
        ).strip()

        if final_content:
            sections.append(
                {
                    "heading": current_heading,
                    "content": final_content,
                }
            )

        return sections

    @staticmethod
    def _build_section_text(
        heading: str,
        content: str,
    ) -> str:
        """
        Include section heading in the embedded content.
        """

        if heading == "document_preamble":
            return content

        return (
            f"Section: {heading}\n\n"
            f"{content}"
        )

    @staticmethod
    def _assign_chunk_ids(
        chunks: list[Document],
    ) -> None:
        """
        Add deterministic chunk IDs.

        Example:
            payment_service__chunk_000
            payment_service__chunk_001
        """

        counters: dict[str, int] = {}

        for chunk in chunks:
            document_id = chunk.metadata.get(
                "document_id",
                "unknown_document",
            )

            current_index = counters.get(
                document_id,
                0,
            )

            chunk.metadata["chunk_id"] = (
                f"{document_id}__chunk_{current_index:03d}"
            )

            counters[document_id] = (
                current_index + 1
            )