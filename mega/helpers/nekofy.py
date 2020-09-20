import aiohttp


class Nekobin:
    def __init__(self):
        self.neko_endpoint = "https://nekobin.com/api/documents"

    async def nekofy(self, payload_content: str):
        async with aiohttp.ClientSession() as nekoSession:
            payload = {"content": payload_content}
            async with nekoSession.post(self.neko_endpoint, data=payload) as resp:
                neko_link = f"https://nekobin.com/{(await resp.json())['result']['key']}.py"
        return neko_link
