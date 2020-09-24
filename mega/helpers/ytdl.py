import os
import json
import time
import logging
import asyncio
import youtube_dl
import humanfriendly as size
from mega.common import Common
from pyrogram.types import Message
from mega.helpers.uploader import UploadFiles
from mega.helpers.nekofy import Nekobin

yt_progress_updates = {}


class YTdl:
    @staticmethod
    async def extract(msg: Message, extraction_type: str):
        ack_message = await msg.reply_text(
            "Trying to download the file to local!"
        )

        temp_dir = os.path.join(Common().working_dir, f"{msg.chat.id}+{msg.message_id}")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        ytdl_options = {}
        if extraction_type == "audio":
            ytdl_options = {
                'format': 'bestaudio/best',
                'noplaylist': 'true',
                'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                'progress_hooks': [YTdl().progress_hooks],
                'ignoreerrors': 'true',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        elif extraction_type == "video":
            ytdl_options = {
                'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[height<=480][ext=m4a]/best',
                'noplaylist': 'true',
                'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                'progress_hooks': [YTdl().progress_hooks],
                'ignoreerrors': 'true',
            }

        yt_progress_updates[f"{msg.chat.id}{msg.message_id}"] = {
            "current": 0,
            "total": 0,
            "file_name": "",
            "last_update": time.time()
        }

        loop = asyncio.get_event_loop()
        yt_process = loop.run_in_executor(None, YTdl().ytdl_download, ytdl_options, msg.text)
        yt_progress = await yt_process

        while True:
            if yt_progress is True:
                temp_file = yt_progress_updates[f"{msg.chat.id}{msg.message_id}"]["file_name"]
                if extraction_type == "audio":
                    file_name = os.path.basename(temp_file)
                    pre, _ = os.path.splitext(file_name)
                    temp_file = os.path.join(temp_dir, f"{pre}.mp3")
                await UploadFiles().upload_file(temp_file, ack_message, msg.text)
                break
            else:
                await asyncio.sleep(1)
                if (time.time() - yt_progress_updates[f"{msg.chat.id}{msg.message_id}"]["last_update"]) > 5:
                    await ack_message.edit_text(
                        f"Downloading: {yt_progress_updates[f'{msg.chat.id}{msg.message_id}']['current']} of "
                        f"{yt_progress_updates[f'{msg.chat.id}{msg.message_id}']['total']}"
                    )
                    yt_progress_updates[f"{msg.chat.id}{msg.message_id}"]["last_update"] = time.time()

    @staticmethod
    def progress_hooks(d):
        try:
            tmp_dir = os.path.basename(os.path.dirname(d["filename"]))
            logging.info(f"downloading file to {tmp_dir}")
            chat_id, message_id = tmp_dir.split("+")
            if d["status"] == "downloading":
                yt_progress_updates[f"{chat_id}{message_id}"]["current"] = size.format_size(
                    int(d["downloaded_bytes"]), binary=True
                )
                yt_progress_updates[f"{chat_id}{message_id}"]["total"] = size.format_size(
                    int(d["total_bytes"]), binary=True
                )
                yt_progress_updates[f"{chat_id}{message_id}"]["file_name"] = d["filename"]
            if d["status"] == "finished":
                # do we need to do this though, anyway to be on a safe side lets keep it too..
                yt_progress_updates[f"{chat_id}{message_id}"]["current"] = size.format_size(
                    int(d["downloaded_bytes"]), binary=True
                )
                yt_progress_updates[f"{chat_id}{message_id}"]["total"] = size.format_size(
                    int(d["total_bytes"]), binary=True
                )
                yt_progress_updates[f"{chat_id}{message_id}"]["file_name"] = d["filename"]
        except Exception as e:
            logging.error(e)

    @staticmethod
    def ytdl_download(ytdl_options: dict, url: str):
        with youtube_dl.YoutubeDL(ytdl_options) as ydl:
            ydl.download([url])
        return True

    @staticmethod
    async def yt_media_info(msg: Message):
        ytdl_options = {}

        with youtube_dl.YoutubeDL(ytdl_options) as ydl:
            video_info = ydl.extract_info(url=msg.text, download=False)

        neko_link = await Nekobin().nekofy(str(json.dumps(video_info, indent=2)))

        return neko_link
