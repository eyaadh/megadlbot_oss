import os
import json
import secrets
import youtube_dl
from mega.common import Common
from pyrogram.types import Message
from mega.helpers.uploader import UploadFiles
from mega.helpers.nekofy import Nekobin


class YTdl:
    @staticmethod
    async def extract_audio(msg: Message):
        # here what we basically do is, create a temp directory for the files to be downloaded,
        temp_dir = os.path.join(Common().working_dir, f"{secrets.token_hex(2)}")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        ack_message = await msg.reply_text(
            "Trying to download the file to local!"
        )

        temp_file = os.path.join(temp_dir, f"{secrets.token_hex(2)}.mp3")

        ytdl_options = {
            'format': 'bestaudio/best',
            'noplaylist': 'true',
            'outtmpl': temp_file,
            'ignoreerrors': 'true',
            'writethumbnail': True,
        }

        with youtube_dl.YoutubeDL(ytdl_options) as ydl:
            ydl.download([msg.text])

        await UploadFiles().upload_file(temp_file, ack_message, msg.text)

    @staticmethod
    async def yt_media_info(msg: Message):
        ytdl_options = {}

        with youtube_dl.YoutubeDL(ytdl_options) as ydl:
            video_info = ydl.extract_info(url=msg.text, download=False)

        neko_link = await Nekobin().nekofy(str(json.dumps(video_info, indent=2)))

        return neko_link
