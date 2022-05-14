import datetime

from disnake.ext import commands, tasks
import disnake

from utility.dataIO import fileIO
import traceback
import sys


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_task.start()
        self.last_timeStamp = datetime.datetime.utcfromtimestamp(0)
        self.old_lst = ['u?close', 'u?ping', 'u?latency', 'u?cleanup', 'u?sell', 'u?shop',
                        'u?buy', 'u?tutorial', 'u?use', 'u?consume', 'u?heal', 'u?equip', 'u?open',
                        'u?opencrate', 'u?open_crate', 'u?crate', 'u?travel', 'u?tv', 'u?spit', 'u?help',
                        'u?reset', 'u?Disable', 'u?disable', 'u?global', 'u?shut', 'u?daily', 'u?Fix', 'u?fix',
                        'u?jishaku', 'u?jsk', 'u?gold', 'u?bal', 'u?balance', 'u?event', 'u?ev', 'u?debug_dat',
                        'u?leaderboard', 'u?lb', 'u?stats', 'u?level', 'u?progress', 'u?lvl', 'u?stat', 'u?profile',
                        'u?change_prefix', 'u?set_prefix', 'u?in_fight', 'u?inventory', 'u?inv', 'u?info', 'u?about',
                        'u?vanish', 'u?supporter', 'u?sp', 'u?vote', 'u?database_count', 'u?fight', 'u?f',
                        'u?boss', 'u?fboss', 'u?bossfight', 'u?clearinv', 'u?invite', 'u?support']

    @tasks.loop(seconds=5)
    async def data_task(self):
        self.bot.items = fileIO("data/items/items.json", "load")
        self.bot.monsters = fileIO("data/stats/monsters.json", "load")
        self.bot.locations = fileIO("data/traveling.json", "load")
        self.bot.crates = fileIO("data/crates.json", "load")
        self.bot.shopping = fileIO("data/shops.json", "load")
        self.bot.boosters = await self.bot.db["boosters"].find_one({"_id": 0})

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Hello!, Thanks for adding me! You can use the command **u?tutorial** To "
                    "know how the bot works!")
                break
    
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

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="This command is on cooldown!",
                description=f"Try again in **{error.retry_after:.2f}** seconds",
                color=disnake.Colour.red(),
            )
            return await inter.send(embed=embed, ephemeral=True)
        raise error

    # @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in self.old_lst:
            embed = disnake.Embed(
                title="We have migrated to slash command!",
                description=("discord has enforced migration to slash command at 2021 summer, on **August 31st 2022**"
                             " all bots should be migrated on time, or they will no longer work\n\n use our bot with"
                             " the default prefix from now on, **/<command>**\n\n*look at the images below for "
                             "demonstration*"
                             ),
                color=disnake.Color.red()
            )
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/827651835372240986/960505423373414400/IMG_0197.png"
            )

            await message.reply(embed=embed)


def setup(bot):
    bot.add_cog(Event(bot))
