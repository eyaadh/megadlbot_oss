import re
import os
from pyrogram import Client, filters, emoji
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply
from mega.telegram import MegaDLBot
from mega.helpers.media_info import MediaInfo
from mega.helpers.downloader import Downloader
from mega.database.users import MegaUsers
from mega.database.files import MegaFiles


@Client.on_message(filters.private & filters.text, group=0)
async def new_message_dl_handler(c: MegaDLBot, m: Message):
    await MegaUsers().insert_user(m.from_user.id)

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(regex, m.text):
        url_count = await MegaFiles().count_files_by_url(m.text)
        if url_count == 0:
            await url_process(m)
        else:
            url_details = await MegaFiles().get_file_by_url(m.text)
            me = await c.get_users("me")
            files = [
                f"<a href='http://t.me/{me.username}?start=plf-{file['file_id']}'>{file['file_name']} - {file['file_type']}</a>"
                for file in url_details
            ]
            files_msg_formatted = '\n'.join(files)

            await m.reply_text(
                f"I also do have the following files that were uploaded earlier with the same url:\n"
                f"{files_msg_formatted}",
                disable_web_page_preview=True,
                quote=True
            )
            await url_process(m)


async def url_process(m: Message):
    header_info = await Downloader.get_headers(m.text)
    file_type_raw = header_info.get("Content-Type") if "Content-Type" in header_info else "None/None"
    file_type_split = file_type_raw.split("/")[0]
    if not header_info:
        await m.reply_text(
            f"I do not know the details of the file to download the file! {emoji.MAN_RAISING_HAND_DARK_SKIN_TONE}", quote=True
        )
    elif header_info:
        file_size = header_info.get("Content-Length") if "Content-Length" in header_info else None
        if not file_size and int(file_size) > 2147483648:
            await m.reply_text(
                f"Well that file is bigger than I can upload to telegram! {emoji.MAN_SHRUGGING_DARK_SKIN_TONE}", quote=True
            )
        else:
            inline_buttons = [
                [
                    InlineKeyboardButton(text=f"{emoji.FLOPPY_DISK} Download",
                                         callback_data=f"download_{m.chat.id}_{m.message_id}"),
                    InlineKeyboardButton(text=f"{emoji.PENCIL} Rename",
                                         callback_data=f"rename_{m.chat.id}_{m.message_id}")
                ]
            ]
            if file_type_split.lower() == "video":
                inline_buttons.append([
                    InlineKeyboardButton(text=f"{emoji.LIGHT_BULB} Media Info",
                                         callback_data=f"info_{m.chat.id}_{m.message_id}")
                ])
            await m.reply_text(
                text="What would you like to do with this file?",
                reply_markup=InlineKeyboardMarkup(inline_buttons),
                quote=True
            )


@Client.on_callback_query(filters.regex("^download.*"), group=0)
async def callback_download_handler(c: MegaDLBot, cb: CallbackQuery):
    cb_chat = int(str(cb.data).split("_")[1]) if len(str(cb.data).split("_")) > 1 else None
    cb_message_id = int(str(cb.data).split("_")[2]) if len(str(cb.data).split("_")) > 2 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()

    await cb.message.delete(True)

    ack_message = await cb_message.reply_text(
        "About to start downloading the file to Local.", quote=True
    )
    await Downloader().download_file(cb_message.text, ack_message, None)
    

@Client.on_callback_query(filters.regex("^rename.*"), group=1)
async def callback_rename_handler(c: MegaDLBot, cb: CallbackQuery):
    await cb.answer()
    cb_message_id = int(str(cb.data).split("_")[2]) if len(str(cb.data).split("_")) > 2 else None
    await cb.message.reply_text(
        f"RENAME_{cb_message_id}:\n"
        f"Send me the new name of the file as a reply to this message.",
        reply_markup=ForceReply(True)
    )


@Client.on_callback_query(filters.regex("^info.*"), group=2)
async def callback_info_handler(c: MegaDLBot, cb: CallbackQuery):
    cb_chat = int(str(cb.data).split("_")[1]) if len(str(cb.data).split("_")) > 1 else None
    cb_message_id = int(str(cb.data).split("_")[2]) if len(str(cb.data).split("_")) > 2 else None

    await cb.answer()
    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None
    m_info, neko_link = await MediaInfo().get_media_info(cb_message.text)
    if m_info:
        try:
            await cb.message.reply_document(
                caption="Here is the Media Info you requested: \n"
                        f"{emoji.CAT} View on nekobin.com: {neko_link}",
                document=m_info
            )
        finally:
            if os.path.exists(m_info):
                os.remove(m_info)

@Client.on_callback_query(filters.regex("cancel_process"), group=3)
async def cancel_download(c: MegaDLBot, cb: CallbackQuery):
    Downloader().cancelled.append(cb.from_user.id)
    await cb.answer("cancelling...")

@Client.on_message(filters.reply & filters.private, group=1)
async def reply_message_handler(c: MegaDLBot, m: Message):
    func_message_obj = str(m.reply_to_message.text).splitlines()[0].split("_")
    if len(func_message_obj) > 1:
        func = func_message_obj[0]
        org_message_id = int(str(func_message_obj[1]).replace(":", ""))
        org_message = await c.get_messages(m.chat.id, org_message_id)
        if func == "RENAME":
            new_file_name = m.text

            ack_message = await m.reply_text(
                "About to start downloading the file to Local."
            )
            await Downloader().download_file(org_message.text, ack_message, new_file_name)
