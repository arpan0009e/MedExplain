from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class KnowledgeDocument:
    """Represents one source document from the medical knowledge base."""

    document_id: str
    title: str
    topic: str
    category: str
    source: str
    source_url: str
    content: str
    file_name: str


class KnowledgeBaseLoader:
    """Loads Markdown documents from the MedExplain knowledge base."""

    def __init__(self, knowledge_base_path: Path):
        self.knowledge_base_path = knowledge_base_path

    def load_documents(self) -> list[KnowledgeDocument]:
        """Load all Markdown knowledge documents."""

        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                f"Knowledge base directory does not exist: "
                f"{self.knowledge_base_path}"
            )

        documents: list[KnowledgeDocument] = []

        for file_path in sorted(self.knowledge_base_path.rglob("*.md")):
            documents.append(self._load_document(file_path))

        return documents

    def _load_document(self, file_path: Path) -> KnowledgeDocument:
        """Load and parse a single Markdown document."""

        content = file_path.read_text(encoding="utf-8")

        metadata = self._extract_metadata(content)

        document_id = file_path.stem

        return KnowledgeDocument(
            document_id=document_id,
            title=metadata["title"],
            topic=metadata["topic"],
            category=metadata["category"],
            source=metadata["source"],
            source_url=metadata["source_url"],
            content=content,
            file_name=file_path.name,
        )

    @staticmethod
    def _extract_metadata(content: str) -> dict[str, str]:
        """Extract metadata from the Markdown document."""

        metadata_fields = {
            "title": r"^#\s+(.+)$",
            "topic": r"^##\s+Topic\s*\n\s*(.+)$",
            "category": r"^##\s+Category\s*\n\s*(.+)$",
            "source": r"^##\s+Source\s*\n\s*(.+)$",
            "source_url": r"^##\s+Source URL\s*\n\s*(.+)$",
        }

        metadata: dict[str, str] = {}

        for field, pattern in metadata_fields.items():
            match = re.search(pattern, content, re.MULTILINE)

            if not match:
                raise ValueError(
                    f"Required metadata field '{field}' "
                    "is missing from the document."
                )

            metadata[field] = match.group(1).strip()

        return metadata