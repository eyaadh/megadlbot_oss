from urllib.parse import quote

import pymongo

from mega.common import Common


class MegaDB:
    def __init__(self):
        DB_USERNAME = Common().db_username
        DB_PASSWORD = Common().db_password

        if DB_USERNAME and DB_PASSWORD:
            connection_string = f"mongodb://{Common().db_username}:{quote(Common().db_password)}@{Common().db_host}"
            self.db_client = pymongo.MongoClient(
                connection_string
            )
        else:
            self.db_client = pymongo.MongoClient(
                Common().db_host,
                username=DB_USERNAME,
                password=DB_PASSWORD
            )

        self.db = self.db_client[Common().db_name]
