from pyrogram.filters import *
from pyrogram.types import CallbackQuery


def callback_query(args: str, payload=True):
    """
    Accepts arg at all times.

    If payload is True, extract payload from callback and assign to callback.payload
    If payload is False, only check if callback exactly matches argument
    """

    async def func(ftl, __, query: CallbackQuery):
        if payload:
            thing = r"{}\_"
            if re.search(re.compile(thing.format(ftl.data)), query.data):
                search = re.search(re.compile(r"\_{1}(.*)"), query.data)
                if search:
                    query.payload = search.group(1)
                else:
                    query.payload = None

                return True

            return False
        else:
            if ftl.data == query.data:
                return True

            return False

    return create(func, 'CustomCallbackQuery', data=args)
