import os
import time
import asyncio
import aiohttp
import logging
import secrets
import aiofiles
import typing
import mimetypes
import urllib.parse
import humanfriendly as size
from pyrogram.types import Message
from mega.telegram import MegaDLBot
from mega.helpers.uploader import UploadFiles
from pyrogram.errors import MessageNotModified, FloodWait

status_progress = {}


class Downloader:
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
                        await dl_file.write(chunk)
                        dl_len += len(chunk)
                        if (time.time() - status_progress[
                                f"{ack_message.chat.id}{ack_message.message_id}"]["last_download_updated"]) > 5:
                            try:
                                await MegaDLBot.edit_message_text(
                                    chat_id=ack_message.chat.id,
                                    message_id=ack_message.message_id,
                                    text=f"Downloading: {file_name} - {size.format_size(dl_len, binary=True)} of "
                                         f"{size.format_size(int(resp.headers.get('Content-Length')), binary=True)}"
                                )
                            except MessageNotModified as e:
                                logging.error(e)
                            except FloodWait as e:
                                logging.error(e)
                                await asyncio.sleep(e.x)

                            status_progress[f"{ack_message.chat.id}{ack_message.message_id}"][
                                "last_download_updated"] = time.time()
        await UploadFiles().upload_file(temp_file, ack_message, url)
