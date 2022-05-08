import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from utility.utils import bcolors

load_dotenv()

DEFAULT_DISABLED_MESSAGE = (
    "The bot is currently disabled for an update or an refresh is happening, please. "
    "wait until its back up, you can join our support server to get notified once its backup."
)


async def is_enabled(ctx):
    if ctx.author.id not in ctx.bot.owner_ids:
        if ctx.bot.ENABLED:
            return True

        await ctx.send(DEFAULT_DISABLED_MESSAGE)
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
        self.shopping = None
        self.BotToken = os.getenv("TOKEN")
        self.TopGGToken = os.getenv("TOPGG_TOKEN")
        self.MongoUrl = os.getenv("MONGO_URL")
        self.invite_url = "https://discord.gg/FQYVpuNz4Q"
        self.vote_url = "https://top.gg/bot/815153881217892372"
        self.currency = "<:doge_coin:864929485295321110>"
        self.add_check(is_enabled)
        self.activity = disnake.Game("Undertale | u?help ")
        self.ENABLED = False
        self.help_command = None
        self.events = None
        self.cmd_list = ["fboss", "bossfight", "boss"]
        self.fights = {}
        self.shops = {}

    async def on_shard_connect(self, shard):
        print(f"{bcolors.GREEN} shard {bcolors.BOLD}{bcolors.CYAN}{shard}{bcolors.ENDC}{bcolors.GREEN} is connected.{bcolors.ENDC}")
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
        self.boosters = self.db["boosters"]
        print("Database connection established")
        print("db_load task finished")
        return


bot = UndertaleBot(
    command_prefix=os.getenv("PREFIX"),
    owner_ids=[
        845322234607829032,
        736820906604888096,
        536538183555481601,
        513351917481623572,
    ]
)

bot.load_extension("jishaku")
bot.run(bot.BotToken)
