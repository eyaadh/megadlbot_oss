import typing
from mega.database import MegaDB


class MegaUsers:
    def __init__(self):
        self.user_collection = MegaDB().db["users"]

    async def insert_user(self, user_id: int):
        if self.user_collection.count({"user_id": user_id}) > 0:
            return False
        else:
            self.user_collection.insert_one(
                {
                    "user_id": user_id,
                    "dld_settings": "default",
                    "custom_thumbnail": None
                }
            )

    async def get_user(self, user_id: int):
        return self.user_collection.find_one({"user_id": user_id})

    async def update_dld_settings(self, user_id: int, data: str):
        self.user_collection.update_one(
            {"user_id": user_id}, {
                "$set": {"dld_settings": data}
            }
        )

    async def update_cst_thumb(self, user_id: int, thumb: typing.Union[bytes, str]):
        self.user_collection.update_one(
            {"user_id": user_id}, {
                "$set": {"custom_thumbnail": thumb}
            }
        )

    async def update_gdrive(self, user_id: int, key_file: typing.Union[bytes, str], key_location: str):
        self.user_collection.update_one(
            {"user_id": user_id}, {
                "$set": {"gdrive_key": key_file, "gdrive_key_location": key_location}
            }
        )
