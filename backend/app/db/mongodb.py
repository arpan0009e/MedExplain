from pymongo.asynchronous.collection import AsyncCollection

from app.core.database import get_database


KNOWLEDGE_CHUNKS_COLLECTION = "knowledge_chunks"


def get_knowledge_chunks_collection() -> AsyncCollection:
    """Return the MongoDB collection used by the RAG knowledge base."""

    database = get_database()

    return database[KNOWLEDGE_CHUNKS_COLLECTION]