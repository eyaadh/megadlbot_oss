import pymongo
from mega.common import Common


class MegaDB:
    def __init__(self):
        self.db_client = pymongo.MongoClient(
            f"mongodb://"
            f"{Common().db_username}:{Common().db_password}@{Common().db_host}"
        )

        self.db = self.db_client[Common().db_name]

        # basically here we are creating/formulating the connection string by getting those values from common
        # obviously with what Warrior has done it fixed the heroku masters had on connecting to mongo
        # what I dont understand is why cant we do the same, as in this where the values are seperately
        # given and formulate the same link? well either way, I am not ready to do this fix, I will
        # need to learn a bit more of heroku and mongo atlas honestly to be able to answer that, either
        # way we will look into that and I am sure @Spechide will raise a good PR I can be proud of
        # haha!!!! listen guys, he is a brilliant developer and has a very good sources shared on both
        # his github and youtube, you should definetly check, I will have them shared at description..
