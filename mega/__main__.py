import asyncio
from aiohttp import web
from pyrogram import idle
from mega.telegram import MegaDLBot
from mega.webserver import web_server
from mega.common import Common


async def main():
    await MegaDLBot.start()
    runner = web.AppRunner(await web_server())
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", Common().web_port).start()
    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
