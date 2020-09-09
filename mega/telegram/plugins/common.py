from pyrogram import filters, emoji
from pyrogram.types import Message
from mega.telegram import MegaDLBot


@MegaDLBot.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: MegaDLBot, m: Message):
    await m.reply_text(
        text=f"Hello! My name is Megatron {emoji.MAN_BOWING_DARK_SKIN_TONE}"
    )
