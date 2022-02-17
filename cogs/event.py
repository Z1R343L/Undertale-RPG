import datetime
import imp
import sys
import traceback

from discord.ext import commands, tasks

import botTools.loader as loader
from botTools.mHelper import bcolors

imp.reload(loader)


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)
        self.updater.start()

    @tasks.loop(seconds=5)
    async def updater(self):
        await self.bot.wait_until_ready()
        await self.bot.db["stats"].update_one(
            {"_id": 0}, {"$set": {"servers": len(self.bot.guilds)}})

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Hello!, Thanks for adding me!, my prefix is **u?**, You can use the command **u?tutorial** To "
                    "know how the bot works!")
                break

    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(f"{bcolors.CYAN}{bcolors.BOLD}{ctx.author}{bcolors.ENDC} Used the command : {bcolors.BOLD}{bcolors.GREEN}{ctx.command} {bcolors.ENDC}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if "Missing Permission" in str(error):
            return
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.message.add_reaction("\N{HOURGLASS}")
        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send("Sorry. This command is disabled and cannot be used.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(
                error,
                (
                        commands.CheckFailure,
                        commands.UserInputError
                ),
        ):
            return
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await self.bot.get_channel(827651947678269510).send(
                f"{error}, {ctx.author.id}, {str(ctx.author)}, {ctx.command}")
            print("\n\n")


def setup(bot):
    bot.add_cog(Event(bot))
