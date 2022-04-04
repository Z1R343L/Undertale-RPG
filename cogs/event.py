import datetime
import importlib

from disnake.ext import commands
import disnake

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
                    "Hello!, Thanks for adding me! You can use the command **/tutorial** To "
                    "know how the bot works!")
                break

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="This command is on cooldown!",
                description=f"Try again in **{error.retry_after:.2f}** seconds",
                color=disnake.Colour.red(),
            )
            await inter.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Event(bot))
