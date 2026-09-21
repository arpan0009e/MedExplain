import asyncio

from app.core.database import initialize_database, close_database
from app.db.mongodb import create_vector_search_index


async def main() -> None:
    await initialize_database()

    try:
        index_name = await create_vector_search_index()
        print(f"Vector Search index created: {index_name}")
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())