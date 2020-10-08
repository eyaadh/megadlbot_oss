import math
import struct
import binascii
from typing import Union
from pyrogram.types import Message
from mega.telegram import MegaDLBot
from pyrogram import Client, utils, raw
from pyrogram.session import Session, Auth
from pyrogram.methods.messages.download_media import FileData
from pyrogram.errors import FileIdInvalid, AuthBytesInvalid


async def chunk_size(length):
    return 2 ** max(min(math.ceil(math.log2(length / 1024)), 10), 2) * 1024


async def offset_fix(offset, chunksize):
    offset -= offset % chunksize
    return offset


class TGCustomYield:
    def __init__(self):
        """TGCustomYield: A custom method to stream files from telegram.

        generate_file_properties: returns the properties for a media on a specific message.

        generate_media_session: returns the media session for the DC that contains the media file on the message.

        yield_file: yield a file from telegram servers for streaming.
        """
        self.main_bot = MegaDLBot

    @staticmethod
    async def generate_file_properties(msg: Message):
        error_message = "This message doesn't contain any downloadable media"
        available_media = ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note")

        media_file_name = None
        file_size = None
        mime_type = None
        date = None

        for kind in available_media:
            media = getattr(msg, kind, None)

            if media is not None:
                break
        else:
            raise ValueError(error_message)

        if isinstance(media, str):
            file_id_str = media
        else:
            file_id_str = media.file_id
            media_file_name = getattr(media, "file_name", "")
            file_size = getattr(media, "file_size", None)
            mime_type = getattr(media, "mime_type", None)
            date = getattr(media, "date", None)
            file_ref = getattr(media, "file_ref", None)

        data = FileData(
            file_name=media_file_name,
            file_size=file_size,
            mime_type=mime_type,
            date=date,
            file_ref=file_ref
        )

        def get_existing_attributes() -> dict:
            return dict(filter(lambda x: x[1] is not None, data.__dict__.items()))

        try:
            decoded = utils.decode_file_id(file_id_str)
            media_type = decoded[0]

            if media_type == 1:
                unpacked = struct.unpack("<iiqqqiiiqi", decoded)
                dc_id, photo_id, _, volume_id, size_type, peer_id, x, peer_access_hash, local_id = unpacked[1:]

                if x == 0:
                    peer_type = "user"
                elif x == -1:
                    peer_id = -peer_id
                    peer_type = "chat"
                else:
                    peer_id = utils.get_channel_id(peer_id - 1000727379968)
                    peer_type = "channel"

                data = FileData(
                    **get_existing_attributes(),
                    media_type=media_type,
                    dc_id=dc_id,
                    peer_id=peer_id,
                    peer_type=peer_type,
                    peer_access_hash=peer_access_hash,
                    volume_id=volume_id,
                    local_id=local_id,
                    is_big=size_type == 3
                )
            elif media_type in (0, 2, 14):
                unpacked = struct.unpack("<iiqqqiiii", decoded)
                dc_id, document_id, access_hash, volume_id, _, _, thumb_size, local_id = unpacked[1:]

                data = FileData(
                    **get_existing_attributes(),
                    media_type=media_type,
                    dc_id=dc_id,
                    document_id=document_id,
                    access_hash=access_hash,
                    thumb_size=chr(thumb_size)
                )
            elif media_type in (3, 4, 5, 8, 9, 10, 13):
                unpacked = struct.unpack("<iiqq", decoded)
                dc_id, document_id, access_hash = unpacked[1:]

                data = FileData(
                    **get_existing_attributes(),
                    media_type=media_type,
                    dc_id=dc_id,
                    document_id=document_id,
                    access_hash=access_hash
                )
            else:
                raise ValueError(f"Unknown media type: {file_id_str}")
            return data
        except (AssertionError, binascii.Error, struct.error):
            raise FileIdInvalid from None

    async def generate_media_session(self, client: Client, msg: Message):
        data = await self.generate_file_properties(msg)

        media_session = client.media_sessions.get(data.dc_id, None)

        if media_session is None:
            if data.dc_id != await client.storage.dc_id():
                media_session = Session(
                    client, data.dc_id, await Auth(client, data.dc_id, await client.storage.test_mode()).create(),
                    await client.storage.test_mode(), is_media=True
                )
                await media_session.start()

                for _ in range(3):
                    exported_auth = await client.send(
                        raw.functions.auth.ExportAuthorization(
                            dc_id=data.dc_id
                        )
                    )

                    try:
                        await media_session.send(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id,
                                bytes=exported_auth.bytes
                            )
                        )
                    except AuthBytesInvalid:
                        continue
                    else:
                        break
                else:
                    await media_session.stop()
                    raise AuthBytesInvalid
            else:
                media_session = Session(
                    client, data.dc_id, await client.storage.auth_key(),
                    await client.storage.test_mode(), is_media=True
                )
                await media_session.start()

            client.media_sessions[data.dc_id] = media_session

        return media_session

    async def yield_file(self, media_msg: Message, offset: int, first_part_cut: int,
                         last_part_cut: int, part_count: int, chunk_size: int) -> Union[str, None]:
        client = self.main_bot
        data = await self.generate_file_properties(media_msg)
        media_session = await self.generate_media_session(client, media_msg)

        current_part = 1

        file_ref = utils.decode_file_ref(data.file_ref)

        if data.media_type == 1:
            if data.peer_type == "user":
                peer = raw.types.InputPeerUser(
                    user_id=data.peer_id,
                    access_hash=data.peer_access_hash
                )
            elif data.peer_type == "chat":
                peer = raw.types.InputPeerChat(
                    chat_id=data.peer_id
                )
            else:
                peer = raw.types.InputPeerChannel(
                    channel_id=data.peer_id,
                    access_hash=data.peer_access_hash
                )

            location = raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=data.volume_id,
                local_id=data.local_id,
                big=data.is_big or None
            )
        elif data.media_type in (0, 2):
            location = raw.types.InputPhotoFileLocation(
                id=data.document_id,
                access_hash=data.access_hash,
                file_reference=file_ref,
                thumb_size=data.thumb_size
            )
        elif data.media_type == 14:
            location = raw.types.InputDocumentFileLocation(
                id=data.document_id,
                access_hash=data.access_hash,
                file_reference=file_ref,
                thumb_size=data.thumb_size
            )
        else:
            location = raw.types.InputDocumentFileLocation(
                id=data.document_id,
                access_hash=data.access_hash,
                file_reference=file_ref,
                thumb_size=""
            )

        r = await media_session.send(
            raw.functions.upload.GetFile(
                location=location,
                offset=offset,
                limit=chunk_size
            ),
        )

        if isinstance(r, raw.types.upload.File):
            while current_part <= part_count:
                chunk = r.bytes
                if not chunk:
                    break
                offset += chunk_size
                if part_count == 1:
                    yield chunk[first_part_cut:last_part_cut]
                    break
                if current_part == 1:
                    yield chunk[first_part_cut:]
                if 1 < current_part < part_count:
                    yield chunk

                r = await media_session.send(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset,
                        limit=chunk_size
                    ),
                )

                current_part += 1
