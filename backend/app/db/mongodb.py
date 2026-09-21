from pymongo import AsyncMongoClient
from pymongo.errors import CollectionInvalid
from pymongo.server_api import ServerApi
from pymongo.operations import SearchIndexModel

from app.core.config import settings


KNOWLEDGE_CHUNKS_COLLECTION = "knowledge_chunks"
VECTOR_INDEX_NAME = "knowledge_chunks_vector_index"


def get_knowledge_chunks_collection():
    """Return the knowledge chunks collection."""

    from app.core.database import get_database

    database = get_database()
    return database[KNOWLEDGE_CHUNKS_COLLECTION]


async def create_vector_search_index() -> str:
    """Create the MongoDB Vector Search index for RAG embeddings."""

    client = AsyncMongoClient(
        settings.mongodb_uri,
        server_api=ServerApi(
            version="1",
            strict=False,
            deprecation_errors=True,
        ),
    )

    try:
        database = client[settings.mongodb_database]

        # Step 1: Make sure the collection exists.
        if KNOWLEDGE_CHUNKS_COLLECTION not in await database.list_collection_names():
            try:
                await database.create_collection(KNOWLEDGE_CHUNKS_COLLECTION)
                print(
                    f"Created collection: {KNOWLEDGE_CHUNKS_COLLECTION}"
                )
            except CollectionInvalid:
                # Another process may have created it between the check
                # and create_collection call.
                pass

        collection = database[KNOWLEDGE_CHUNKS_COLLECTION]

        await collection.create_index(
        [("chunk_id", 1)],
        unique=True,
        name="chunk_id_unique_idx",
)

        # Step 2: Define the vector index.
        index = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 384,
                        "similarity": "cosine",
                    }
                ]
            },
            name=VECTOR_INDEX_NAME,
            type="vectorSearch",
        )

        # Step 3: Create the vector index.
        result = await collection.create_search_index(
            model=index
        )

        return result

    finally:
        await client.close()