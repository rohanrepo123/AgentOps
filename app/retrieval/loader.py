from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".md", ".txt"}


class KnowledgeBaseLoader:
    """
    Loads AcmeCloud knowledge-base documents and preserves
    document metadata from YAML-style front matter.
    """

    def __init__(
        self,
        knowledge_base_dir: Path,
    ) -> None:
        self.knowledge_base_dir = Path(
            knowledge_base_dir
        )

    def load(self) -> list[Document]:
        if not self.knowledge_base_dir.exists():
            raise FileNotFoundError(
                f"Knowledge base not found: "
                f"{self.knowledge_base_dir}"
            )

        documents: list[Document] = []

        for path in sorted(
            self.knowledge_base_dir.rglob("*")
        ):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            documents.append(
                self._load_file(path)
            )

        if not documents:
            raise RuntimeError(
                "No documents found in knowledge base."
            )

        return documents

    def _load_file(
        self,
        path: Path,
    ) -> Document:

        raw_content = path.read_text(
            encoding="utf-8"
        )

        frontmatter, body = (
            self._parse_frontmatter(
                raw_content
            )
        )

        relative_path = (
            path.relative_to(
                self.knowledge_base_dir
            )
        )

        directory_category = (
            relative_path.parts[0]
            if len(relative_path.parts) > 1
            else "unknown"
        )

        # --------------------------------------------------
        # Metadata priority:
        #
        # front matter
        #       ↓
        # inferred value
        #       ↓
        # fallback
        # --------------------------------------------------

        category = frontmatter.get(
            "category"
        ) or self._normalize_category(
            directory_category
        )

        document_id = (
            frontmatter.get("document_id")
            or path.stem
        )

        document_type = (
            frontmatter.get("document_type")
            or self._infer_document_type(
                category,
                directory_category,
            )
        )

        service = frontmatter.get(
            "service"
        )

        # Convert meaningless values to None.
        if service in {
            None,
            "",
            "mixed",
            "platform",
            "unknown",
        }:
            service = None

        metadata: dict[str, Any] = {
            "source": str(relative_path).replace(
                "\\",
                "/",
            ),
            "document_id": document_id,
            "category": category,
            "document_type": document_type,
        }

        if service:
            metadata["service"] = service

        for field in [
            "version",
            "incident_id",
            "severity",
        ]:
            value = frontmatter.get(field)

            if value:
                metadata[field] = value

        return Document(
            page_content=body,
            metadata=metadata,
        )

    @staticmethod
    def _parse_frontmatter(
        content: str,
    ) -> tuple[dict[str, str], str]:

        if not content.startswith("---"):
            return {}, content

        lines = content.splitlines()

        if len(lines) < 3:
            return {}, content

        closing_index = None

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_index = i
                break

        if closing_index is None:
            return {}, content

        metadata: dict[str, str] = {}

        for line in lines[
            1:closing_index
        ]:

            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            metadata[
                key.strip()
            ] = value.strip()

        body = "\n".join(
            lines[
                closing_index + 1:
            ]
        ).lstrip()

        return metadata, body

    @staticmethod
    def _normalize_category(
        directory_category: str,
    ) -> str:

        mapping = {
            "architecture": "architecture",
            "services": "service",
            "api_docs": "api_docs",
            "runbooks": "runbook",
            "troubleshooting": "troubleshooting",
            "incident_reports": "incident_report",
        }

        return mapping.get(
            directory_category,
            directory_category,
        )

    @staticmethod
    def _infer_document_type(
        category: str,
        directory_category: str,
    ) -> str:

        mapping = {
            "architecture": "architecture",
            "service": "service_documentation",
            "services": "service_documentation",
            "api_docs": "api_documentation",
            "runbook": "runbook",
            "runbooks": "runbook",
            "troubleshooting": "troubleshooting",
            "incident_report": "historical_incident",
            "incident_reports": "historical_incident",
        }

        return mapping.get(
            category,
            mapping.get(
                directory_category,
                "unknown",
            ),
        )

data = KnowledgeBaseLoader(knowledge_base_dir=r'D:\Study_IIITN\CampusX\Project Agent\data')
# data_fetch = data.load()
# for data_1 in data_fetch:
#     print(i.metadata['source'])