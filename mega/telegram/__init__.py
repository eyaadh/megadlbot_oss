from pyrogram import Client
from .utils import filters
from mega.common import Common

if Common().is_env:
    MegaDLBot = Client(
        api_id=Common().tg_app_id,
        api_hash=Common().tg_api_key,
        session_name=Common().bot_session,
        bot_token=Common().bot_api_key,
        workers=200,
        workdir=Common().working_dir,
        plugins=dict(root="mega/telegram/plugins")
    )
else:
    MegaDLBot = Client(
        session_name=Common().bot_session,
        bot_token=Common().bot_api_key,
        workers=200,
        workdir=Common().working_dir,
        config_file=Common().app_config_file
    )
