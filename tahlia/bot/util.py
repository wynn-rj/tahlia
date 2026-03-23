import uuid
from pathlib import Path

import aiohttp
from discord.ext import commands
from PIL import Image

from tahlia.bot.entry import BotMessageException
from tahlia.util import IMAGE_DIR


def _new_image_path():
    for _ in range(10000):
        if not (path := IMAGE_DIR.joinpath(str(uuid.uuid4()))).exists():
            path.touch()
            return path
    raise BotMessageException('Image folder full')


async def _download_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            path = _new_image_path()
            with open(path, mode="wb") as file:
                while (chunk := await response.content.read()):
                    file.write(chunk)
            return path


def _assert_is_image(path: Path):
    try:
        Image.open(path).verify()
    except Exception as ex:
        raise BotMessageException('Attached file is not a valid image') from ex


async def _get_image_from_embed_url(url: str):
    try:
        path = await _download_file(url)
    except Exception as ex:
        raise BotMessageException('Unable to download attached image') from ex
    _assert_is_image(path)
    return path


async def get_image_from_message(ctx: commands.Context):
    message = await ctx.message.fetch()
    print([x.type for x in message.embeds])
    if (embeds := list(filter(lambda c: c.type == 'image', message.embeds))):
        return await _get_image_from_embed_url(embeds[0].url)
    if not message.attachments:
        raise BotMessageException('An image must be supplied with this command')

    path = _new_image_path()
    await message.attachments[0].save(path)
    _assert_is_image(path)
    return path
