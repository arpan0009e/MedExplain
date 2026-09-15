from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import database


class ReportRepository:
    """Database operations for medical reports."""

    collection = database["reports"]

    async def create(
        self,
        filename: str,
    ) -> dict:
        """Create a new report document."""

        document = {
            "filename": filename,
            "status": "uploaded",
            "created_at": datetime.now(timezone.utc),
        }

        result = await self.collection.insert_one(document)

        document["_id"] = result.inserted_id

        return document