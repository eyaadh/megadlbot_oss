import os
import logging
import shutil
import asyncio
import secrets
import pathlib
from mega.common import Common
from pyrogram.types import Message


class Screens:
    @staticmethod
    async def cap_screens(msg: Message):
        link = msg.text
        duration_process_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", link]

        process = await asyncio.create_subprocess_exec(*duration_process_cmd, stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)

        duration, _ = await process.communicate()

        duration_int = int(float(duration.decode("utf-8").rstrip()))

        tmp_dir = os.path.join(pathlib.Path().absolute(),
                               Common().working_dir, secrets.token_hex(2))
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

            for x in range(4):
                shot_duration = int(duration_int * ((x + 1) / 5))
                tmp_file = os.path.join(tmp_dir, f"{secrets.token_hex(2)}.jpg")

                screen_cap_process_cmd = ["ffmpeg", "-ss", f"{shot_duration}", "-i",
                                          link, "-vframes", "1", "-q:v", "2", tmp_file]
                screen_process = await asyncio.create_subprocess_exec(*screen_cap_process_cmd,
                                                                      stdout=asyncio.subprocess.PIPE,
                                                                      stderr=asyncio.subprocess.PIPE)
                data, err = await screen_process.communicate()

                if os.path.isfile(tmp_file):
                    await msg.reply_photo(
                        photo=tmp_file,
                        caption=f"Screen capture at {shot_duration} second."
                    )

            try:
                shutil.rmtree(tmp_dir)
            except Exception as e:
                logging.error(e)
