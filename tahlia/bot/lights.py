import discord
from discord.ext import commands
from StreamDeck.Devices.StreamDeck import StreamDeck

from tahlia.bot.util import get_image_from_message
from tahlia.lights.scene import SceneManager
from tahlia.stream_deck.integration import SwitchSceneKey
from tahlia.stream_deck.pages import Page
from tahlia.stream_deck.util import load_image
from tahlia.util import update_layout_file


class SceneManagerCog(commands.Cog):

    def __init__(self, bot: commands.Bot, manager: SceneManager, light_page: Page):
        self.bot = bot
        self.manager = manager
        self.page = light_page

    @commands.group(pass_context=True)
    async def scene(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help('scene')

    @scene.command()
    async def list(self, ctx: commands.Context):
        self.manager.refresh()
        scenes = "\n - ".join(self.manager.names_to_id.keys())
        await ctx.send(f' - {scenes}')

    @scene.command()
    async def bind(self, ctx: commands.Context, scene: str):
        self.manager.refresh()
        if not self.manager.has_scene(scene):
            return await ctx.send(f"Unknown scene '{scene}'")
        image_path = await get_image_from_message(ctx)
        with update_layout_file('lights.json') as layout:
            layout.append({'type': 'scene', 'scene': scene, 'image': image_path.name})
        image = load_image(self.page.deck, str(image_path))
        self.page.add_key(SwitchSceneKey(image, self.manager, scene))
        await ctx.send('Bound scene to stream deck')
