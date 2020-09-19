from urllib.parse import quote

import pymongo

from mega.common import Common


class MegaDB:
    def __init__(self):
        if Common().is_atlas:
            self.db_client = pymongo.MongoClient(
                Common().db_host,
            )
        else:
            self.db_client = pymongo.MongoClient(
                Common().db_host,
                username=Common().db_username,
                password=Common().db_password
            )

        self.db = self.db_client[Common().db_name]
