from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import get_database


class ReportRepository:
    """Database operations for medical reports."""

    @property
    def collection(self):
        """Return the reports collection from the active database."""

        return get_database()["reports"]

    async def create(self, filename: str) -> dict:
        """Create a new report document."""

        document = {
            "filename": filename,
            "status": "uploaded",
            "created_at": datetime.now(timezone.utc),
        }

        result = await self.collection.insert_one(document)

        document["_id"] = result.inserted_id

        return document

    async def get_by_id(self, report_id: str) -> dict | None:
        """Find a report by its MongoDB ObjectId."""

        if not ObjectId.is_valid(report_id):
            return None

        return await self.collection.find_one(
            {"_id": ObjectId(report_id)}
        )