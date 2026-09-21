import asyncio
from pathlib import Path

from app.core.database import initialize_database, close_database
from app.rag.ingestion import KnowledgeBaseIngestion


KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[1] / "knowledge_base"
)


async def main() -> None:
    await initialize_database()

    try:
        ingestion = KnowledgeBaseIngestion(
            knowledge_base_path=KNOWLEDGE_BASE_PATH
        )

        count = await ingestion.ingest()

        print(
            f"Knowledge-base ingestion completed. "
            f"Chunks inserted or updated: {count}"
        )

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())