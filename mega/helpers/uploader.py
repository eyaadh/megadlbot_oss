import asyncio
import base64
import logging
import mimetypes
import os
import secrets
import shutil
import time

import aiofiles
import humanfriendly as size
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import Message

from mega.common import Common
from mega.database.files import MegaFiles
from mega.database.users import MegaUsers
from mega.telegram import MegaDLBot
from mega.helpers.gdrive import Gdrive

status_progress = {}
msg_caption = ""


class UploadFiles:
    @staticmethod
    async def upload_file(temp_file: str, ack_message: Message, url: str, upload_type: str):
        file_type = mimetypes.guess_type(temp_file)
        await MegaDLBot.edit_message_text(
            chat_id=ack_message.chat.id,
            message_id=ack_message.message_id,
            text="About to upload the file to Telegram..."
        )
        status_progress[f"{ack_message.chat.id}{ack_message.message_id}"] = {"last_upload_updated": time.time()}
        try:
            user_details = await MegaUsers().get_user(ack_message.chat.id)
            if user_details['dld_settings'] == 'default':
                if str(file_type[0]).split("/")[0].lower() == "audio":
                    file_message = await MegaDLBot.send_audio(
                        chat_id=ack_message.chat.id,
                        audio=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id]
                    )

                    await UploadFiles().send_file_to_dustbin(file_message, "audio", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                else:
                    file_message = await MegaDLBot.send_document(
                        chat_id=ack_message.chat.id,
                        document=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id]
                    )

                    await UploadFiles().send_file_to_dustbin(file_message, "doc", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
            elif user_details['dld_settings'] == 'f-docs':
                if str(file_type[0]).split("/")[0].lower() == "audio":
                    file_message = await MegaDLBot.send_audio(
                        chat_id=ack_message.chat.id,
                        audio=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id]
                    )

                    await UploadFiles().send_file_to_dustbin(file_message, "audio", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                else:
                    file_message = await MegaDLBot.send_document(
                        chat_id=ack_message.chat.id,
                        document=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id]
                    )
                    await UploadFiles().send_file_to_dustbin(file_message, "doc", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
            elif user_details['dld_settings'] == 'ct-docs':
                temp_thumb = await UploadFiles().get_thumbnail(user_details['custom_thumbnail'])
                if str(file_type[0]).split("/")[0].lower() == "audio":
                    file_message = await MegaDLBot.send_audio(
                        chat_id=ack_message.chat.id,
                        audio=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )

                    await UploadFiles().send_file_to_dustbin(file_message, "audio", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                else:
                    file_message = await MegaDLBot.send_document(
                        chat_id=ack_message.chat.id,
                        document=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )
                    await UploadFiles().send_file_to_dustbin(file_message, "doc", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)
            elif user_details['dld_settings'] == 'ct-videos':
                temp_thumb = await UploadFiles().get_thumbnail(user_details['custom_thumbnail'])

                if str(file_type[0]).split("/")[0].lower() == "video":
                    file_message = await MegaDLBot.send_video(
                        chat_id=ack_message.chat.id,
                        video=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )
                    await UploadFiles().send_file_to_dustbin(file_message, "video", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                elif str(file_type[0]).split("/")[0].lower() == "audio":
                    file_message = await MegaDLBot.send_audio(
                        chat_id=ack_message.chat.id,
                        audio=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )

                    await UploadFiles().send_file_to_dustbin(file_message, "audio", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                else:
                    file_message = await MegaDLBot.send_document(
                        chat_id=ack_message.chat.id,
                        document=temp_file,
                        progress=UploadFiles().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )
                    await UploadFiles().send_file_to_dustbin(file_message, "doc", url)
                    await UploadFiles().handle_gdrive(file_message, ack_message, temp_file)
                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)

        finally:
            if upload_type != "compressed":
                await MegaDLBot.delete_messages(
                    chat_id=ack_message.chat.id,
                    message_ids=ack_message.message_id
                )

                if os.path.exists(temp_file):
                    # we are just going to remove this file & its folder from our local, since its useless at local now
                    try:
                        shutil.rmtree(os.path.dirname(temp_file))
                    except Exception as e:
                        logging.error(str(e))

    @staticmethod
    async def send_file_to_dustbin(file_message: Message, media_type: str, url: str):
        global msg_caption
        fd_msg = await file_message.forward(
            chat_id=Common().bot_dustbin,
            as_copy=True
        )
        file_link = f"https://{Common().web_fqdn}/{fd_msg.message_id}" if Common().on_heroku else \
            f"http://{Common().web_fqdn}:{Common().web_port}/{fd_msg.message_id}"

        msg_caption = f"Here is the Streaming <a href='{file_link}'>link</a> for this file."

        await file_message.edit_text(
            text=msg_caption,
            parse_mode="html",
            disable_web_page_preview=True
        )

        if media_type == "video":
            await MegaFiles().insert_new_files(
                filed_id=fd_msg.video.file_id,
                file_name=fd_msg.video.file_name,
                msg_id=fd_msg.message_id,
                chat_id=fd_msg.chat.id,
                file_type=fd_msg.video.mime_type,
                url=url
            )
        elif media_type == "audio":
            await MegaFiles().insert_new_files(
                filed_id=fd_msg.audio.file_id,
                file_name=fd_msg.audio.file_name,
                msg_id=fd_msg.message_id,
                chat_id=fd_msg.chat.id,
                file_type=fd_msg.audio.mime_type,
                url=url
            )
        else:
            await MegaFiles().insert_new_files(
                filed_id=fd_msg.document.file_id,
                file_name=fd_msg.document.file_name,
                msg_id=fd_msg.message_id,
                chat_id=fd_msg.chat.id,
                file_type=fd_msg.document.mime_type,
                url=url
            )

    @staticmethod
    async def upload_progress_hook(current, total, chat_id, message_id):
        if (time.time() - status_progress[f"{chat_id}{message_id}"]["last_upload_updated"]) > 5:
            try:
                await MegaDLBot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"Uploading - {size.format_size(current, binary=True)} of {size.format_size(total, binary=True)}"
                )
            except MessageNotModified as e:
                logging.error(e)
            except FloodWait as e:
                logging.error(e)
                await asyncio.sleep(e.x)

            status_progress[f"{chat_id}{message_id}"][
                "last_upload_updated"] = time.time()

    @staticmethod
    async def get_thumbnail(data: bytes):
        temp_file = f"mega/working_dir{secrets.token_hex(2)}.jpg"
        async with aiofiles.open(temp_file, mode='wb') as temp_thumb:
            await temp_thumb.write(base64.decodebytes(data))
        return temp_file

    @staticmethod
    async def handle_gdrive(file_msg: Message, ack_msg: Message, temp_file: str):
        global msg_caption
        gfile = await Gdrive().upload_file(ack_msg.chat.id, temp_file)
        if gfile:
            glink = f"https://drive.google.com/file/d/{gfile.get('id')}"
            await file_msg.edit_text(
                f"{msg_caption}\nHere is the gdrive <a href={glink}> link</a>, this link might expire in 12hrs",
                parse_mode="html",
                disable_web_page_preview=True
            )
