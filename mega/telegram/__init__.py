from pyrogram import Client
from mega.common import Common

MegaDLBot = Client(
    session_name=Common().bot_session,
    bot_token=Common().bot_api_key,
    workers=200,
    workdir=Common().working_dir,
    config_file=Common().app_config_file
)
