import asyncio

from pyrogram import idle

from mega.telegram import MegaDLBot


async def main():
    await MegaDLBot.start()
    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
