import datetime
import importlib

from disnake.ext import commands

import utility.loader as loader

importlib.reload(loader)


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Hello!, Thanks for adding me!, my prefix is **u?**, You can use the command **u?tutorial** To "
                    "know how the bot works!")
                break

def setup(bot):
    bot.add_cog(Event(bot))
