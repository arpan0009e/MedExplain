import asyncio

from app.core.database import initialize_database, close_database
from app.rag.retriever import KnowledgeRetriever


TEST_QUERIES = [
    "What is hemoglobin?",
    "What does LDL mean?",
    "What does HbA1c measure?",
]


async def main() -> None:
    await initialize_database()

    try:
        retriever = KnowledgeRetriever()

        for query in TEST_QUERIES:
            print("\n" + "=" * 80)
            print(f"QUERY: {query}")
            print("=" * 80)

            results = await retriever.search(
                query=query,
                top_k=3,
            )

            if not results:
                print("No results found.")
                continue

            for index, result in enumerate(results, start=1):
                print(f"\nRESULT {index}")
                print(f"Chunk ID: {result.chunk_id}")
                print(f"Document ID: {result.document_id}")
                print(f"Score: {result.score:.4f}")
                print(f"Source: {result.metadata.get('source')}")
                print(f"Title: {result.metadata.get('title')}")
                print("\nText:")
                print(result.text[:500])

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())