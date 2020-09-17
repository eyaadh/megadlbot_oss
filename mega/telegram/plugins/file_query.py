from pyrogram import emoji, Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton

from mega.database.files import MegaFiles


@Client.on_inline_query()
async def inline_query_handler(c: Client, iq: InlineQuery):
    q = iq.query
    q_res_data = await MegaFiles().get_file_by_name(q)
    me = await c.get_me()
    res = []
    if q_res_data is not None:
        for file in q_res_data:
            res.append(
                InlineQueryResultArticle(
                    title=file['file_name'],
                    description=f"{file['file_name']} - {file['file_type']}",
                    thumb_url="https://cdn3.iconfinder.com/data/icons/education-vol-1-34/512/15_File_files_office-256"
                              ".png",
                    input_message_content=InputTextMessageContent(
                        message_text=f"{file['file_name']} - {file['file_type']}"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(text=f"{emoji.OPEN_MAILBOX_WITH_LOWERED_FLAG} Get this File",
                                                  url=f"http://t.me/{me.username}?start=plf-{file['file_id']}")]
                        ]
                    )
                )
            )

    if len(res) > 0:
        await iq.answer(
            results=res,
            cache_time=0,
            is_personal=False
        )
