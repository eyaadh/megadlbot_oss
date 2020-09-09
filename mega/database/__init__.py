import pymongo
from mega.common import Common


class MegaDB:
    def __init__(self):
        self.db_client = pymongo.MongoClient(
            f"mongodb://"
            f"{Common().db_username}:{Common().db_password}@{Common().db_host}"
        )

        self.db = self.db_client[Common().db_name]