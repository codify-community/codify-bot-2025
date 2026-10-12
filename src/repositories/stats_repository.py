from pymongo.results import UpdateResult

from .connection import client


class StatsRepository:
    def __init__(self) -> None:
        self.collection = client["stats"]["general"]

    async def fetch_users_stats(self) -> list[dict[str, str]]:
        stats = self.collection.find_one({"_id": "0"})

        staffs = [
            staff for staff in stats["specialMembers"] if staff["role"] != "booster"
        ]
        boosters = [
            staff for staff in stats["specialMembers"] if staff["role"] == "booster"
        ]

        return staffs, boosters

    async def update(
        self,
        channel_count: int,
        member_count: int,
        specialMembers: list[dict[str, str]],
    ) -> UpdateResult:
        if not self.collection.find_one({"_id": "0"}):
            return self.collection.insert_one(
                {
                    "_id": "0",
                    "channelCount": channel_count,
                    "memberCount": member_count,
                    "specialMembers": specialMembers,
                }
            )

        return self.collection.update_one(
            {"_id": "0"},
            {
                "$set": {
                    "channelCount": channel_count,
                    "memberCount": member_count,
                    "specialMembers": specialMembers,
                }
            },
        )
