import os
import json
import time
import logging
import aiohttp
import secrets
import aiofiles
import humanfriendly as size
from mega.common import Common
from pyrogram.types import Message
from mega.helpers.uploader import UploadFiles
from pyrogram.errors import MessageNotModified

seedr_status_progress = {}


class SeedrAPI:
    def __init__(self):
        self.web_dav = "https://www.seedr.cc/rest"
        self.username = Common().seedr_username
        self.sdpwd = Common().seedr_password

    async def add_url(self, url: str, link_type: str):
        async with aiohttp.ClientSession() as seedr_session:
            endpoint = f"{self.web_dav}/torrent/magnet" if link_type == "magnet" else f"{self.web_dav}/torrent/url"
            data = {"magnet": url} if link_type == "magnet" else {"torrent_url": url}
            async with seedr_session.post(
                        url=endpoint,
                        data=data,
                        auth=aiohttp.BasicAuth(
                            self.username,
                            self.sdpwd
                        )
                    ) as resp:
                return json.loads(await resp.text())

    async def get_torrent_details(self, torrent_id: str):
        async with aiohttp.ClientSession() as seedr_session:
            endpoint = f"{self.web_dav}/torrent/{torrent_id}"
            async with seedr_session.get(
                        url=endpoint,
                        auth=aiohttp.BasicAuth(
                            self.username,
                            self.sdpwd
                        )
                    ) as resp:
                return json.loads(await resp.text())
    async def get_folder(self, folder_id: str):
        async with aiohttp.ClientSession() as seedr_session:
            endpoint = f"{self.web_dav}/folder/{folder_id}"
            async with seedr_session.get(
                        url=endpoint,
                        auth=aiohttp.BasicAuth(
                            self.username,
                            self.sdpwd
                        )
                    ) as resp:
                return json.loads(await resp.text())
    async def delete_folder(self, folder_id: str):
        async with aiohttp.ClientSession() as seedr_session:
            endpoint = f"{self.web_dav}/folder/{folder_id}"
            async with seedr_session.delete(
                            url=endpoint,
                            auth=aiohttp.BasicAuth(
                                self.username,
                                self.sdpwd
                            )
                    ) as resp:
                return json.loads(await resp.text())
    async def download_folder(self, folder_id: str, ack_message: Message, org_message: Message):
    async def download_folder(self, folder_id: str, ack_message: Message, org_message: Message):
        endpoint = f"{self.web_dav}/folder/{folder_id}/download"
        temp_dir = os.path.join(Common().working_dir, secrets.token_hex(2))
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        folder_details = await self.get_folder(folder_id)
        dl_folder_name = f"{folder_details['name']}.zip"
        dl_compressed_file = os.path.join(temp_dir, dl_folder_name)
        await ack_message.edit_reply_markup(None)

        seedr_status_progress[f"{ack_message.chat.id}{ack_message.message_id}"] = {"last_updated": time.time()}

        async with aiohttp.ClientSession() as seedr_session:
            async with seedr_session.get(
                            url=endpoint,
                            auth=aiohttp.BasicAuth(
                                self.username,
                                self.sdpwd
                            )
                    ) as resp:
                async with aiofiles.open(dl_compressed_file, mode="wb") as fd:
                    downloaded = 0

                    async for chunk in resp.content.iter_any():
                        downloaded += len(chunk)
                        await fd.write(chunk)

                        if (time.time() - seedr_status_progress[f"{ack_message.chat.id}{ack_message.message_id}"]["last_updated"]) > 5:
                            try:
                                await ack_message.edit_text(
                                    f"Downloading file to local: {size.format_size(downloaded, binary=True)}"
                                )

                                seedr_status_progress[f"{ack_message.chat.id}{ack_message.message_id}"]["last_updated"] = time.time()
                            except MessageNotModified as e:
                                logging.error(e)
        await UploadFiles().upload_file(dl_compressed_file, ack_message, org_message.text)