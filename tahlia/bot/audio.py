import discord
from discord.ext import commands
from StreamDeck.Devices.StreamDeck import StreamDeck

from tahlia.audio.spotify import SpotifyAudioClient
from tahlia.bot.entry import BotMessageException
from tahlia.bot.util import (
    _download_file,
    _get_image_from_embed_url,
    get_image_from_message,
)
from tahlia.lights.scene import SceneManager
from tahlia.stream_deck.integration import (
    AudioPlayPlaylistKey,
    SwitchSceneKey,
    WindowImageKey,
)
from tahlia.stream_deck.pages import Page
from tahlia.stream_deck.util import load_image
from tahlia.util import update_layout_file


class AudioManagerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, music_page: Page, client: SpotifyAudioClient):
        self.bot = bot
        self.page = music_page
        self.client = client

    @commands.group(pass_context=True)
    async def audio(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("window")

    @audio.command()
    async def bind(self, ctx: commands.Context, url: str, label: str = ""):
        if (
            context := self.client.retrive_context(url)
        ) is None or "uri" not in context:
            await ctx.send("Unexpected url value")
            return
        if not label or label in [e.url for e in ctx.message.embeds]:
            if (label := context.get("name", None)) is None:
                await ctx.send("Unable to retrieve name from audio link")
                return
        try:
            image_path = await get_image_from_message(ctx)
        except BotMessageException:
            if not context.get("images", None):
                await ctx.send("Unable to retrieve image from audio link")
                return
            try:
                image_path = await _download_file(context["images"][0]["url"])
            except:
                await ctx.send("Unable to retrieve image from audio link")
                return
        with update_layout_file("music.json") as layout:
            layout.append(
                {
                    "type": "playlist",
                    "label": label,
                    "image": image_path.name,
                    "uri": context["uri"],
                }
            )
        image = load_image(self.page.deck, str(image_path))
        self.page.add_key(
            AudioPlayPlaylistKey(image, self.client, label, context["uri"])
        )
        await ctx.send("Bound audio to stream deck")
