import configparser


class Common:
    def __init__(self):
        self.app_config = configparser.ConfigParser()

        self.app_config_file = "mega/working_dir/config.ini"
        self.working_dir = "mega/working_dir"
        self.app_config.read(self.app_config_file)

        self.bot_session = self.app_config.get("bot-configuration", "session")
        self.bot_api_key = self.app_config.get("bot-configuration", "api_key")

        self.db_host = self.app_config.get("database", "db_host")
        self.db_username = self.app_config.get("database", "db_username")
        self.db_password = self.app_config.get("database", "db_password")
        self.db_name = self.app_config.get("database", "db_name")