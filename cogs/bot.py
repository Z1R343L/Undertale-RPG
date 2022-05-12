import time

import aiohttp
import disnake
from disnake.ext import commands, tasks

from utility.dataIO import fileIO

starttime = time.time()


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        headers = {"Authorization": self.bot.TopGGToken}
        self.dbl_session = aiohttp.ClientSession(headers=headers)
        self.post_dbl.start()
        self.set_event.start()

    @tasks.loop(seconds=10)
    async def set_event(self):
        data = fileIO("event.json", "load")
        if data["name"] is not None:
            self.bot.events = data
        else:
            return

    @tasks.loop(minutes=5)
    async def post_dbl(self):
        await self.bot.wait_until_ready()
        data = {"server_count": len(self.bot.guilds), "shard_count": len(self.bot.shards)}
        await self.dbl_session.post(f"https://top.gg/api/bots/{self.bot.user.id}/stats", data=data)

    @commands.command(aliases=["ev"])
    async def event(self, inter):
        event = self.bot.events
        if event is None:
            await inter.send("There is no event ongoing at the moment.")
            self.bot.events = None
            return

        name = event["name"]
        banner = event["banner"]
        desc = event["desc"]

        embed = disnake.Embed(
            title=f"{name} Event",
            description=desc,
            colour=disnake.Colour.random()
        )
        embed.set_image(url=banner)
        await inter.send(embed=embed)

    @commands.command(aliases=["about"])
    async def info(self, inter):
        """information about the bot and more"""
        em = disnake.Embed(color=disnake.Colour.random())

        em.title = "Undertale RPG"
        em.description = "An Undertale RPG Themed bot for discord, Made by LetsChill#0001"

        em.add_field(
            name="links",
            value="[Support Server](https://discord.gg/FQYVpuNz4Q)\n[top.gg link](https://top.gg/bot/815153881217892372)")
        em.add_field(
            name="Guilds Count",
            value=f"`{len(self.bot.guilds)}` Guilds",
            inline=False)

        em.add_field(
            name="Latency",
            value=f"`{round(self.bot.latency * 1000)}`ms",
            inline=False)

        em.add_field(
            name="current shard/shard count",
            value=f"{inter.guild.shard_id}/{len(self.bot.shards)}",
            inline=False
        )
        em.set_thumbnail(url=self.bot.user.avatar.url)
        await inter.send(embed=em)

    @commands.command()
    async def vote(self, inter):
        """Vote for the bot for special reward"""
        vt = disnake.Embed(title="<:DT:865088692376829952> Voting", color=0x2ECC71)
        vt.add_field(
            name="Vote on Top.gg (500G + Standard crate)",
            value=f"[Click Here]({self.bot.vote_url})",
            inline=True,
        )
        vt.add_field(
            name="Claim and support our server",
            value="You can claim an exclusive reward by joining our server and running u?supporter",
            inline=True,
        )
        await inter.send(embed=vt)

    @commands.command(aliases=["support"])
    async def invite(self, inter):
        """Invite the bot!!!"""
        e = disnake.Embed(
            title="Wanna add me to your server huh?, click the link below!",
            color=disnake.Colour.blue(),
        )
        e.add_field(
            name="Invite Bot",
            value=("[Click Here]"
                "(https://discord.com/api/oauth2/authorize?client_id=815153881217892372&permissions=412421053760&scope="
                   "bot%20applications.commands)"),
        )

        e.add_field(
            name="Join server", value="[Click Here](https://discord.gg/FQYVpuNz4Q)"
        )

        e.set_thumbnail(url=self.bot.user.avatar.url)
        await inter.send(embed=e)

    @commands.slash_command()
    async def ping(self, inter):
        """Latency Check for stability"""
        await inter.send(f"pong! **{round(self.bot.latency * 1000)}ms**")


def setup(bot):
    bot.add_cog(Bot(bot))
