from pyrogram import Client
from mega.common import Common

MegaDLBot = Client(
    session_name=Common().bot_session,
    bot_token=Common().bot_api_key,
    workers=200,
    workdir=Common().working_dir,
    if Common().is_env:
        plugins=dict(root="mega/telegram/plugins"))
    else:
        config_file=Common().app_config_file
)
