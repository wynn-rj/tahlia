import discord
from discord.ext import commands
from StreamDeck.Devices.StreamDeck import StreamDeck

from tahlia.bot.util import get_image_from_message
from tahlia.lights.scene import SceneManager
from tahlia.stream_deck.integration import SwitchSceneKey, WindowImageKey
from tahlia.stream_deck.pages import Page
from tahlia.stream_deck.util import load_image
from tahlia.util import update_layout_file


class WindowManagerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, window_page: Page):
        self.bot = bot
        self.page = window_page

    @commands.group(pass_context=True)
    async def window(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("window")

    @window.command()
    async def bind(self, ctx: commands.Context, label: str):
        image_path = await get_image_from_message(ctx)
        if (embeds := ctx.message.embeds) and embeds[0].url == label:
            await ctx.send("Missing required argument label")
            image_path.unlink()
            return
        with update_layout_file("window.json") as layout:
            layout.append({"type": "window", "label": label, "image": image_path.name})
        image = load_image(self.page.deck, str(image_path))
        self.page.add_key(WindowImageKey(image, label, str(image_path)))
        await ctx.send("Bound window to stream deck")
