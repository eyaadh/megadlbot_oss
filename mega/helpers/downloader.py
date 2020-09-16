import os
import time
import base64
import aiohttp
import secrets
import aiofiles
import shutil
import typing
import logging
import mimetypes
import urllib.parse
import humanfriendly as size
from pyrogram.types import Message
from pyrogram import emoji
from mega.telegram import MegaDLBot
from mega.database.users import MegaUsers
from mega.database.files import MegaFiles
from mega.common import Common
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

status_progress = {}


class Downloader:
    cancelled = []
    
    @staticmethod
    async def get_headers(url: str):
        async with aiohttp.ClientSession() as mega_session:
            async with mega_session.get(url) as resp:
                return resp.headers

    @staticmethod
    async def download_file(url: str, ack_message: Message, new_file_name: typing.Union[None, str]):
        async with aiohttp.ClientSession() as mega_session:
            async with mega_session.get(url) as resp:
                temp_dir = f"mega/working_dir/{secrets.token_hex(2)}"
                if not os.path.exists(temp_dir):
                    os.mkdir(temp_dir)

                # first lets try getting the file name from link, which mostly works
                file_name = urllib.parse.unquote(
                    os.path.basename(urllib.parse.urlparse(url).path)) if new_file_name is None else new_file_name
                if file_name is None:
                    guessed_extension = mimetypes.guess_extension(resp.headers.get("Content-Type"))
                    file_name = f"{secrets.token_hex(2)}{guessed_extension}"

                temp_file = os.path.join(temp_dir, file_name)

                async with aiofiles.open(temp_file, mode="wb") as dl_file:
                    dl_len = 0
                    status_progress[f"{ack_message.chat.id}{ack_message.message_id}"] = {
                        "last_download_updated": time.time()
                    }
                    async for chunk in resp.content.iter_any():
                        if ack_message.chat.id in Downloader().cancelled:
                            await MegaDLBot.edit_message_text(
                                chat_id=ack_message.chat.id,
                                message_id=ack_message.message_id,
                                text = "Cancelled successfully"
                            )
                            Downloader().cancelled.remove(ack_message.chat.id) # reset
                            os.remove(temp_file)
                            break
                        await dl_file.write(chunk)
                        dl_len += len(chunk)
                        if (time.time() - status_progress[
                                f"{ack_message.chat.id}{ack_message.message_id}"]["last_download_updated"]) > 5:
                            await MegaDLBot.edit_message_text(
                                chat_id=ack_message.chat.id,
                                message_id=ack_message.message_id,
                                text=f"Downloading: {file_name} - {size.format_size(dl_len, binary=True)} of "
                                     f"{size.format_size(int(resp.headers.get('Content-Length')), binary=True)}",
                                reply_markup=InlineKeyboardMarkup(
                                    [[ 
                                       InlineKeyboardButton("cancel " + emoji.MULTIPLY,callback_data=f"cancel_process")
                                    ]]
                               )                         
                            )

                            status_progress[f"{ack_message.chat.id}{ack_message.message_id}"][
                                "last_download_updated"] = time.time()
        await Downloader().upload_file(temp_file, ack_message, url)

    @staticmethod
    async def upload_file(temp_file: str, ack_message: Message, url: str):
        if not os.path.isfile(temp_file):
            return
        await MegaDLBot.edit_message_text(
            chat_id=ack_message.chat.id,
            message_id=ack_message.message_id,
            text="About to upload the file to Telegram..."
        )
        status_progress[f"{ack_message.chat.id}{ack_message.message_id}"][
            "last_upload_updated"] = time.time()
        try:
            user_details = await MegaUsers().get_user(ack_message.chat.id)
            if user_details['dld_settings'] == 'default':
                file_message = await MegaDLBot.send_document(
                    chat_id=ack_message.chat.id,
                    document=temp_file,
                    progress=Downloader().upload_progress_hook,
                    progress_args=[ack_message.chat.id, ack_message.message_id]
                )

                await Downloader().send_file_to_dustbin(file_message, "doc", url)

            elif user_details['dld_settings'] == 'f-docs':
                file_message = await MegaDLBot.send_document(
                    chat_id=ack_message.chat.id,
                    document=temp_file,
                    progress=Downloader().upload_progress_hook,
                    progress_args=[ack_message.chat.id, ack_message.message_id]
                )
                await Downloader().send_file_to_dustbin(file_message, "doc", url)
            elif user_details['dld_settings'] == 'ct-docs':
                temp_thumb = await Downloader().get_thumbnail(user_details['custom_thumbnail'])
                file_message = await MegaDLBot.send_document(
                    chat_id=ack_message.chat.id,
                    document=temp_file,
                    progress=Downloader().upload_progress_hook,
                    progress_args=[ack_message.chat.id, ack_message.message_id],
                    thumb=temp_thumb
                )
                await Downloader().send_file_to_dustbin(file_message, "doc", url)

                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)
            elif user_details['dld_settings'] == 'ct-videos':
                file_type = mimetypes.guess_type(temp_file)
                temp_thumb = await Downloader().get_thumbnail(user_details['custom_thumbnail'])

                if str(file_type[0]).split("/")[0].lower() == "video":
                    file_message = await MegaDLBot.send_video(
                        chat_id=ack_message.chat.id,
                        video=temp_file,
                        progress=Downloader().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )
                    await Downloader().send_file_to_dustbin(file_message, "video", url)
                else:
                    file_message = await MegaDLBot.send_document(
                        chat_id=ack_message.chat.id,
                        document=temp_file,
                        progress=Downloader().upload_progress_hook,
                        progress_args=[ack_message.chat.id, ack_message.message_id],
                        thumb=temp_thumb
                    )
                    await Downloader().send_file_to_dustbin(file_message, "doc", url)

                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)

        finally:
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
        if media_type == "video":
            await file_message.forward(
                chat_id=Common().bot_dustbin,
                as_copy=True
            )
            await MegaFiles().insert_new_files(
                filed_id=file_message.video.file_id,
                file_name=file_message.video.file_name,
                msg_id=file_message.message_id,
                chat_id=file_message.chat.id,
                file_type=file_message.video.mime_type,
                url=url
            )
        else:
            await file_message.forward(
                chat_id=Common().bot_dustbin,
                as_copy=True
            )
            await MegaFiles().insert_new_files(
                filed_id=file_message.document.file_id,
                file_name=file_message.document.file_name,
                msg_id=file_message.message_id,
                chat_id=file_message.chat.id,
                file_type=file_message.document.mime_type,
                url=url
            )

    @staticmethod
    async def upload_progress_hook(current, total, chat_id, message_id):
        if (time.time() - status_progress[f"{chat_id}{message_id}"]["last_upload_updated"]) > 5:
            await MegaDLBot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Uploading - {size.format_size(current, binary=True)} of {size.format_size(total, binary=True)}"
            )

    @staticmethod
    async def get_thumbnail(data: bytes):
        temp_file = f"mega/working_dir{secrets.token_hex(2)}.jpg"
        async with aiofiles.open(temp_file, mode='wb') as temp_thumb:
            await temp_thumb.write(base64.decodebytes(data))
        return temp_file
