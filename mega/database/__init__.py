import pymongo
from mega.common import Common


class MegaDB:
    def __init__(self):
        self.db_client = pymongo.MongoClient(
            f"{Common().db_url}"
        )
        self.db = self.db_client[Common().db_name]
