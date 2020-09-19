import os
import secrets
import youtube_dl
from mega.common import Common
from pyrogram.types import Message
from mega.helpers.uploader import UploadFiles


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
