import configparser
import os


class Common:
    def __init__(self):
        self.working_dir = "mega/working_dir"

        self.is_env = bool(os.environ.get("ENV", None))
        if self.is_env:
            self.tg_app_id = int(os.environ.get("TG_APP_ID"))
            self.tg_api_key = os.environ.get("TG_API_HASH")

            self.bot_session = ":memory:"
            self.bot_api_key = os.environ.get("TG_BOT_TOKEN")
            self.bot_dustbin = int(os.environ.get("TG_DUSTBIN_CHAT", "-100"))

            self.db_uri = os.environ.get("DATABASE_URI")
            self.db_name = os.environ.get("DATABASE_DB_NAME")
        else:
            self.app_config = configparser.ConfigParser()

            self.app_config_file = "mega/working_dir/config.ini"
            self.app_config.read(self.app_config_file)

            self.tg_app_id = int(self.app_config.get("pyrogram", "api_id"))
            self.tg_api_key = self.app_config.get("pyrogram", "api_hash")

            self.bot_session = self.app_config.get("bot-configuration", "session")
            self.bot_api_key = self.app_config.get("bot-configuration", "api_key")
            self.bot_dustbin = int(self.app_config.get("bot-configuration", "dustbin"))

            self.db_uri = self.app_config.get("database", "db_uri")
            self.db_name = self.app_config.get("database", "db_name")
