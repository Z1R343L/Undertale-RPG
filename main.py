import logging
import os

import discord
from discord.ext import commands
from dislash import InteractionClient
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from botTools.loader import _create_guild_info
from botTools.mHelper import bcolors

load_dotenv()
FORMAT = f"{bcolors.WARNING} %(levelname)s : {bcolors.ENDC}" \
         f" %(name)s %(filename)s {bcolors.BOLD}%(message)s {bcolors.ENDC} "

logging.basicConfig(level=logging.INFO, format=FORMAT)


async def is_enabled(ctx):
    if ctx.author.id not in ctx.bot.owner_ids:
        if ctx.bot.ENABLED:
            return True

        await ctx.send(ctx.bot.WARNING)
        return False
    return True


class UndertaleBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guilds_db = None
        self.players = None
        self.cluster = None
        self.db = None
        self.players = None
        self.db = None
        self.cluster = None
        self.BotToken = os.getenv("TOKEN")
        self.TopGGToken = os.getenv("TOPGG_TOKEN")
        self.MongoUrl = os.getenv("MONGO_URL")
        self.invite_url = "https://discord.gg/FQYVpuNz4Q"
        self.vote_url = "https://top.gg/bot/815153881217892372"
        self.currency = "<:doge_coin:864929485295321110>"
        self.WARNING = "The bot is currently disabled for an update or an refresh is happening, please " \
                       "wait until its back up, you can join our support server to get notified once its backup. "
        self.add_check(is_enabled)
        self.activity = discord.Game("Undertale | u?help ")
        self.ENABLED = False
        self.help_command = None
        self.events = None
        self.cmd_list = ["fboss", "bossfight", "boss"]

    async def on_shard_connect(self, shard):
        print(f"{bcolors.GREEN} shard id:{shard} is connected.{bcolors.ENDC}")
        if shard == 0:
            await self.db_load()
            await self.load_all_cogs()

    async def load_all_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                self.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔁 {bcolors.GREEN}{bcolors.BOLD}cogs.{filename[:-3]} is loaded and ready.{bcolors.ENDC}")
        self.ENABLED = True
        return

    async def db_load(self):
        await self.wait_until_ready()
        self.cluster = AsyncIOMotorClient(self.MongoUrl)
        self.db = self.cluster["database"]
        self.players = self.db["players"]
        self.guilds_db = self.db["guilds"]
        print("Database connection established")
        print("db_load task finished")
        return

    # To access to stuff

    # @property
    # def mongo(self):
    #    return self.get_cog("Mongo")


async def determine_prefix(UT, message):
    if bot.ENABLED is False:
        return "u?"
    if message.guild:
        data = await _create_guild_info(UT, message.guild)
        return data["prefix"]
    return "u?"


bot = UndertaleBot(
    command_prefix=determine_prefix,
    owner_ids=[
        845322234607829032,
        736820906604888096,
        536538183555481601,
        513351917481623572,
    ],
)

bot.slash = InteractionClient(bot)
bot.load_extension("jishaku")
bot.run(bot.BotToken)
