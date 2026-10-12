from datetime import UTC, datetime, timedelta

import pymongo

from .connection import client


class UnbanRequestsRepository:
    def __init__(self):
        self.collection = client["codify"]["unban"]

    async def create(self, user_id: int) -> dict:
        unban_request_with_same_user_id = await self.find_unban_request(user_id=user_id)
        if unban_request_with_same_user_id:
            return unban_request_with_same_user_id

        unban_request = {
            "_id": user_id,
            "createdAt": datetime.now(UTC),
        }

        self.collection.insert_one(unban_request)
        return unban_request

    async def get_unban_requests(self, limit: int = 100) -> list:
        one_day_ago = datetime.now(UTC) - timedelta(days=1)

        cursor = self.collection.find({"createdAt": {"$lt": one_day_ago}}).sort(
            "createdAt", pymongo.DESCENDING
        )

        return cursor.to_list(length=limit)

    async def find_unban_request(self, user_id: int) -> dict | None:
        return self.collection.find_one({"_id": user_id})

    async def delete_unban_request(self, user_id: int) -> None:
        self.collection.delete_one(
            {"_id": user_id},
        )
