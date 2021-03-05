import os
import re
import secrets
import asyncio
import logging
import tldextract
import humanfriendly as size
from mega.common import Common
from pyrogram import emoji, Client
from mega.helpers.ytdl import YTdl
from mega.helpers.screens import Screens
from mega.database.files import MegaFiles
from mega.database.users import MegaUsers
from mega.helpers.seerd_api import SeedrAPI
from pyrogram.errors import MessageNotModified
from mega.helpers.media_info import MediaInfo
from mega.helpers.uploader import UploadFiles
from mega.helpers.downloader import Downloader
from mega.telegram.utils.custom_download import TGCustomYield
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply

from ..utils import filters

youtube_dl_links = ["youtube", "youtu", "facebook", "soundcloud"]


@Client.on_message(filters.private & filters.text, group=0)
async def new_message_dl_handler(c: Client, m: Message):
    await MegaUsers().insert_user(m.from_user.id)
    user_details = await MegaUsers().get_user(m.from_user.id)

    me = await c.get_me()

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(regex, m.text) or m.text.startswith("magnet"):
        url_count = await MegaFiles().count_files_by_url(m.text)
        if url_count == 0 and not m.text.startswith("magnet"):
            await url_process(m)
        elif url_count == 0 and m.text.startswith("magnet"):
            if ('seedr_username' in user_details) and ('seedr_passwd' in user_details):
                await call_seedr_download(m, "magnet")
            else:
                await m.reply_text("Well! I do not know how to download torrents unless you connect me to Seedr. "
                                   "Seedr Settings are available under /dldsettings")
        elif m.text.startswith("magnet"):
            url_details = await MegaFiles().get_file_by_url(m.text)
            files = [
                f"<a href='http://t.me/{me.username}?start=plf-{file['_id']}'>{file['file_name']}"
                f" - {file['file_type']}</a>"
                for file in url_details
            ]
            files_msg_formatted = '\n'.join(files)

            await m.reply_text(
                f"I also do have the following files that were uploaded earlier with the same url:\n"
                f"{files_msg_formatted}",
                disable_web_page_preview=True
            )
            await url_process(m)
        else:
            url_details = await MegaFiles().get_file_by_url(m.text)
            files = [
                f"<a href='http://t.me/{me.username}"
                f"?start=plf-{file['_id']}'>{file['file_name']} - {file['file_type']}</a>"
                for file in url_details
            ]
            files_msg_formatted = '\n'.join(files)

            await m.reply_text(
                f"I also do have the following files that were uploaded earlier with the same url:\n"
                f"{files_msg_formatted}",
                disable_web_page_preview=True
            )

            await url_process(m)


async def url_process(m: Message):
    user_details = await MegaUsers().get_user(m.from_user.id)

    if m.text.startswith("magnet"):
        await m.reply_text(
            text="What would you like to do with this file?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=f"{emoji.MAGNET} Proceed with Download",
                                          callback_data=f"magnet_{m.chat.id}_{m.message_id}")]
                ]
            )
        )
    else:
        header_info = await Downloader.get_headers(m.text)
        file_type_raw = header_info.get("Content-Type") if "Content-Type" in header_info else "None/None"
        file_type_split = file_type_raw.split("/")[0]
        file_content_disposition = header_info.get("content-disposition")
        try:
            file_name_f_headers = re.findall("filename=(.+)", file_content_disposition)[
                0] if file_content_disposition else None
        except Exception as e:
            logging.error(e)
            file_name_f_headers = None

        file_ext_f_name = os.path.splitext(str(file_name_f_headers).replace('"', ""))[1]

        if header_info is None:
            await m.reply_text(
                f"I do not know the details of the file to download the file! {emoji.MAN_RAISING_HAND_DARK_SKIN_TONE}"
            )
        elif (tldextract.extract(m.text)).domain not in youtube_dl_links:
            file_size = header_info.get("Content-Length") if "Content-Length" in header_info else None
            if file_size is not None and int(file_size) > 2147483648:
                await m.reply_text(
                    f"Well that file is bigger than I can upload to telegram! {emoji.MAN_SHRUGGING_DARK_SKIN_TONE}"
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
                                             callback_data=f"info_{m.chat.id}_{m.message_id}"),
                        InlineKeyboardButton(text=f"{emoji.FRAMED_PICTURE} Screens",
                                             callback_data=f"screens_{m.chat.id}_{m.message_id}")
                    ])
                elif file_ext_f_name == ".torrent" and ('seedr_username' in user_details) and \
                        ('seedr_passwd' in user_details):
                    inline_buttons.append([
                        InlineKeyboardButton(text=f"{emoji.TORNADO} Download Torrent",
                                             callback_data=f"torrent_{m.chat.id}_{m.message_id}")
                    ])
                await m.reply_text(
                    text="What would you like to do with this file?",
                    reply_markup=InlineKeyboardMarkup(inline_buttons)
                )
        elif (tldextract.extract(m.text)).domain in youtube_dl_links:
            inline_buttons = [
                [
                    InlineKeyboardButton(text=f"{emoji.LOUDSPEAKER} Extract Audio",
                                         callback_data=f"ytaudio_{m.chat.id}_{m.message_id}"),
                    InlineKeyboardButton(text=f"{emoji.VIDEOCASSETTE} Extract Video",
                                         callback_data=f"ytvid_{m.chat.id}_{m.message_id}")
                ],
                [
                    InlineKeyboardButton(text=f"{emoji.LIGHT_BULB} Media Info",
                                         callback_data=f"ytmd_{m.chat.id}_{m.message_id}")
                ]
            ]
            await m.reply_text(
                text="What would you like to do with this file?",
                reply_markup=InlineKeyboardMarkup(inline_buttons)
            )


@Client.on_callback_query(filters.callback_query("ytvid"), group=0)
async def callback_ytvid_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await YTdl().extract(cb_message, "video")


@Client.on_callback_query(filters.callback_query("ytaudio"), group=0)
async def callback_ytaudio_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await YTdl().extract(cb_message, "audio")


@Client.on_callback_query(filters.callback_query("ytmd"), group=0)
async def callback_ytmd_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    video_info = await YTdl().yt_media_info(cb_message)

    await cb_message.reply_text(
        "Here is the Media Info you requested: \n"
        f"{emoji.CAT} View on nekobin.com: {video_info}"
    )


@Client.on_callback_query(filters.callback_query("torrent"), group=0)
async def callback_torrent_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await call_seedr_download(cb_message, "other")


@Client.on_callback_query(filters.callback_query("magnet"), group=0)
async def callback_magnet_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()
    await call_seedr_download(cb_message, "magnet")


@Client.on_callback_query(filters.callback_query("download"), group=0)
async def callback_download_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None

    await cb.answer()

    ack_message = await cb_message.reply_text(
        "About to start downloading the file to Local."
    )

    await Downloader().download_file(cb_message.text, ack_message, None)


@Client.on_callback_query(filters.callback_query("screens"), group=0)
async def callback_screens_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

    cb_message = await c.get_messages(cb_chat, cb_message_id) if cb_message_id is not None else None
    await Screens().cap_screens(cb_message)
    # i think that should do... lets check?


@Client.on_callback_query(filters.callback_query("rename"), group=1)
async def callback_rename_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    cb_message_id = int(params[1]) if len(params) > 1 else None

    await cb.message.reply_text(
        f"RENAME_{cb_message_id}:\n"
        f"Send me the new name of the file as a reply to this message.",
        reply_markup=ForceReply(True)
    )


@Client.on_callback_query(filters.callback_query("info"), group=2)
async def callback_info_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')
    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None

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


@Client.on_message(filters.reply & filters.private, group=1)
async def reply_message_handler(c: Client, m: Message):
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


@Client.on_callback_query(filters.callback_query("sdlc"), group=2)
async def callback_sdlc_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    folder_id = params[0] if len(params) > 0 else None
    chat_id = int(params[1]) if len(params) > 1 else None
    org_msg_id = int(params[2]) if len(params) > 2 else None
    ack_msg_id = int(params[3]) if len(params) > 3 else None

    org_msg = await c.get_messages(chat_id, org_msg_id)
    ack_msg = await c.get_messages(chat_id, ack_msg_id)

    folder_details = await SeedrAPI().get_folder(folder_id, cb.message.chat.id)
    await SeedrAPI().download_folder(folder_details['id'], ack_msg, org_msg, "other")


@Client.on_callback_query(filters.callback_query("unsd"), group=2)
async def callback_unsd_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    folder_id = params[0] if len(params) > 0 else None
    chat_id = int(params[1]) if len(params) > 1 else None
    org_msg_id = int(params[2]) if len(params) > 2 else None
    ack_msg_id = int(params[3]) if len(params) > 3 else None

    org_msg = await c.get_messages(chat_id, org_msg_id)
    ack_msg = await c.get_messages(chat_id, ack_msg_id)

    folder_details = await SeedrAPI().get_folder(folder_id, cb.message.chat.id)
    await SeedrAPI().download_folder(folder_details['id'], ack_msg, org_msg, "compressed")


async def call_seedr_download(msg: Message, torrent_type: str):
    if torrent_type == "magnet":
        ack_msg = await msg.reply_text(
            "About to add the magnet link to seedr."
        )

        tr_process = await SeedrAPI().add_url(msg.text, "magnet", msg.chat.id)
    else:
        ack_msg = await msg.reply_text(
            "About to add the link to seedr."
        )
        tr_process = await SeedrAPI().add_url(msg.text, "other", msg.chat.id)

    if tr_process["result"] is True:
        try:
            while True:
                await asyncio.sleep(4)
                tr_progress = await SeedrAPI().get_torrent_details(tr_process["user_torrent_id"], msg.chat.id)
                if tr_progress["progress"] < 100:
                    try:
                        await ack_msg.edit_text(
                            f"Uploading to Seedr: \n"
                            f"Progress: {tr_progress['progress']}% | "
                            f"Size: {size.format_size(tr_progress['size'], binary=True)}"
                        )
                    except MessageNotModified as e:
                        logging.error(e)
                else:
                    await asyncio.sleep(10)
                    tr_progress = await SeedrAPI().get_torrent_details(tr_process["user_torrent_id"], msg.chat.id)
                    await ack_msg.edit_text("How would you like to upload the contents?")
                    await ack_msg.edit_reply_markup(
                        InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(text=f"{emoji.PACKAGE} Compressed",
                                                         callback_data=f"sdlc_{str(tr_progress['folder_created'])}"
                                                                       f"_{msg.chat.id}_{msg.message_id}"
                                                                       f"_{ack_msg.message_id}")
                                ],
                                [
                                    InlineKeyboardButton(text=f"{emoji.CARD_FILE_BOX} UnCompressed",
                                                         callback_data=f"unsd_{str(tr_progress['folder_created'])}"
                                                                       f"_{msg.chat.id}_{msg.message_id}"
                                                                       f"_{ack_msg.message_id}")
                                ]
                            ]
                        )
                    )
                    break
        except Exception as e:
            logging.error(e)
    else:
        try:
            error = tr_process['error']
        except KeyError:
            error = None

        logging.error(error)
        await ack_msg.edit_text(
            f"An error occurred:\n<pre>{error}</pre>",
            parse_mode="html"
        )


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio), group=4)
async def media_receive_handler(c: Client, m: Message):
    user_settings = await MegaUsers().get_user(m.from_user.id)
    if "f_rename_type" not in user_settings:
        await MegaUsers().update_file_rename_settings(m.from_user.id, "disk")

    fd_msg = await m.copy(
        chat_id=Common().bot_dustbin
    )

    file_link = f"https://{Common().web_fqdn}/{fd_msg.message_id}" if Common().on_heroku else \
        f"http://{Common().web_fqdn}:{Common().web_port}/{fd_msg.message_id}"

    await m.reply_text(
        text="What would you like to do with this file?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"{emoji.ROCKET} Streaming Link", url=file_link)],
                [InlineKeyboardButton(text=f"{emoji.PEN} Rename File",
                                      callback_data=f"prflrn_{m.chat.id}_{m.message_id}")]
            ]
        )
    )


@Client.on_callback_query(filters.callback_query("prflrn"), group=1)
async def callback_file_rename_proc_handler(c: Client, cb: CallbackQuery):
    await cb.answer()

    params = cb.payload.split('_')
    cb_message_id = int(params[1]) if len(params) > 1 else None

    await cb.message.reply_text(
        text=f"FRNM_{cb_message_id}\n"
             "Send me the new name of this file to rename it.",
        reply_markup=ForceReply(True)
    )


@Client.on_message(filters.reply & filters.text, group=5)
async def reply_media_rename_handler(c: Client, m: Message):
    user_settings = await MegaUsers().get_user(m.from_user.id)

    func_message_obj = str(m.reply_to_message.text).splitlines()[0].split("_")
    if len(func_message_obj) > 1:
        func = func_message_obj[0]

        if func == "FRNM":
            org_message_id = int(str(func_message_obj[1]).replace(":", ""))
            org_message = await c.get_messages(m.chat.id, org_message_id)
            ack_msg = await m.reply_text(
                "Processing to file to rename it."
            )
            if "f_rename_type" in user_settings:
                if user_settings["f_rename_type"] == "memory":
                    m_file = await TGCustomYield().download_as_bytesio(org_message)
                    await UploadFiles().upload_file(m_file, ack_msg, "", "other", "bytesIO", m.text)
                else:
                    temp_dir = f"working_dir/{secrets.token_hex(2)}"
                    if not os.path.exists(f"mega/{temp_dir}"):
                        os.mkdir(f"mega/{temp_dir}")

                    m_file = f"{temp_dir}/{m.text}"

                    await c.download_media(
                        message=org_message,
                        file_name=m_file
                    )

                    await UploadFiles().upload_file(f"mega/{m_file}", ack_msg, "", "other", "disk", m.text)
