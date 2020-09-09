import os
import json
import asyncio
import secrets
import aiofiles
import aiohttp
from mega.common import Common


class MediaInfo:
    @staticmethod
    async def get_media_info(file: str):
        neko_endpoint = "https://nekobin.com/api/documents"
        process_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file]
        process = await asyncio.create_subprocess_exec(*process_cmd, stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE)

        data, err = await process.communicate()
        m_info = json.loads(data.decode("utf-8").rstrip())

        if m_info is None:
            return False
        else:
            temp_file = os.path.join(Common().working_dir, f"{secrets.token_hex(2)}.txt")
            async with aiofiles.open(temp_file, mode="w") as m_file:
                await m_file.write(str(json.dumps(m_info, indent=2)))

            neko_link = ""

            async with aiohttp.ClientSession() as nekoSession:
                payload = {"content": str(json.dumps(m_info, indent=2))}
                async with nekoSession.post(neko_endpoint, data=payload) as resp:
                    neko_link = f"https://nekobin.com/{(await resp.json())['result']['key']}.py"

        return temp_file, neko_link
