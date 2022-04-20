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
        self.old_lst = ['u?close', 'u?ping', 'u?latency', 'u?cleanup', 'u?sell', 'u?shop',
                        'u?buy', 'u?tutorial', 'u?use', 'u?consume', 'u?heal', 'u?equip', 'u?open',
                        'u?opencrate', 'u?open_crate', 'u?crate', 'u?travel', 'u?tv', 'u?spit', 'u?help',
                        'u?reset', 'u?Disable', 'u?disable', 'u?global', 'u?shut', 'u?daily', 'u?Fix', 'u?fix',
                        'u?jishaku', 'u?jsk', 'u?gold', 'u?bal', 'u?balance', 'u?event', 'u?ev', 'u?debug_dat',
                        'u?leaderboard', 'u?lb', 'u?stats', 'u?level', 'u?progress', 'u?lvl', 'u?stat', 'u?profile',
                        'u?change_prefix', 'u?set_prefix', 'u?in_fight', 'u?inventory', 'u?inv', 'u?info', 'u?about',
                        'u?vanish', 'u?supporter', 'u?sp', 'u?vote', 'u?database_count', 'u?fight', 'u?f',
                        'u?boss', 'u?fboss', 'u?bossfight', 'u?clearinv', 'u?invite', 'u?support']

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
