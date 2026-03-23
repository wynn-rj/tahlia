import logging
import os

import discord
from discord.ext import commands

_log = logging.getLogger(__name__)


class BotMessageException(Exception):

    def __init__(self, message: str):
        self.message = message


async def setup():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord')

    bot.on_command_error

    @bot.event
    async def on_command_error(context: commands.Context, exception: Exception):
        if (command := context.command) and command.has_error_handler():
            return

        if (cog := context.cog) and cog.has_error_handler():
            return

        if isinstance(exception, commands.CommandInvokeError):
            exception = exception.original

        if isinstance(exception, commands.CommandNotFound):
            return

        if isinstance(exception, BotMessageException):
            await context.send(exception.message)
            return

        if isinstance(exception, commands.MissingRequiredArgument):
            await context.send(exception.args[0])
            return

        await context.send('An unexpected exception occurred')
        _log.error('Unhandled exception in command %s', command, exc_info=exception)

    return bot
