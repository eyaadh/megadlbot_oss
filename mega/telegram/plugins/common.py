from pyrogram import filters, emoji, Client
from pyrogram.types import Message
from mega.database.files import MegaFiles


@Client.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: Client, m: Message):
    if len(m.command) > 1:
        if m.command[1].split("-")[0] == 'plf':
            file_id = m.command[1].split("-", 1)[1]
            file_details = await MegaFiles().get_file_by_file_id(file_id)

            if file_details is not None:
                file_message = await c.get_messages(
                    chat_id=file_details['chat_id'],
                    message_ids=file_details['msg_id']
                )

                if str(file_details['file_type'].split("/"))[0].lower() == "video":
                    await m.reply_video(
                        video=file_message.video.file_id,
                        file_ref=file_message.video.file_ref
                    )
                else:
                    await m.reply_document(
                        document=file_message.document.file_id,
                        file_ref=file_message.document.file_ref
                    )
    else:
        await m.reply_text(
            text=f"Hello! My name is Megatron {emoji.MAN_BOWING_DARK_SKIN_TONE}"
        )
