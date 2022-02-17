import time
from typing import Counter

import aiohttp
import discord
from discord.ext import commands, tasks

from botTools.dataIO import fileIO
from botTools.loader import create_guild_info

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
    async def event(self, ctx):
        event = self.bot.events
        if event is None:
            await ctx.send("There is no event ongoing at the moment.")
            self.bot.events = None
            return

        name = event["name"]
        banner = event["banner"]
        desc = event["desc"]

        embed = discord.Embed(
            title=f"{name} Event",
            description=desc,
            colour=discord.Colour.random()
        )
        embed.set_image(url=banner)
        await ctx.send(embed=embed)

    @commands.command(aliases=["set_prefix"])
    @commands.has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, *, prefix):
        if len(prefix) >= 8:
            return await ctx.send("You can't set a prefix higher than 8 characters.")

        data = await create_guild_info(ctx, ctx.guild)
        data["prefix"] = prefix
        await ctx.bot.guilds_db.update_one({"_id": ctx.guild.id}, {"$set": data})
        return await ctx.send(f"Changed prefix to {prefix}")

    @commands.command(aliases=["about"])
    async def info(self, ctx):
        """information about the bot and more"""
        em = discord.Embed(color=discord.Colour.random())

        em.title = "Undertale RPG"
        em.description = "An Undertale RPG Themed bot for discord, Made by LetsChill#0001"

        em.add_field(
            name="links",
            value="[Support Server](https://discord.gg/FQYVpuNz4Q)\n[Wiki Link](https://undertale-rpg.fandom.com/)\n[top.gg link](https://top.gg/bot/815153881217892372)")
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
            value=f"{ctx.guild.shard_id}/{len(self.bot.shards)}",
            inline=False
        )
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=em)

    @commands.command()
    async def vote(self, ctx):
        """Vote for the bot for special reward"""
        vt = discord.Embed(title="<:DT:865088692376829952> Voting", color=0x2ECC71)
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
        await ctx.send(embed=vt)

    @commands.command(aliases=["support"])
    async def invite(self, ctx):
        """Invite the bot!!!"""
        e = discord.Embed(
            title="Wanna add me to your server huh?, click the link below!",
            color=discord.Colour.blue(),
        )
        e.add_field(
            name="Invite Bot",
            value="[Click Here](https://discord.com/api/oauth2/authorize?client_id=815153881217892372&permissions=388160&scope=bot)",
        )

        e.add_field(
            name="Join server", value="[Click Here](https://discord.gg/FQYVpuNz4Q)"
        )

        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)

    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        """Latency Check for stability"""
        before = time.monotonic()
        message = await ctx.send("Pinging!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong! {int(ping)}ms")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel."""

        def check(m):
            return m.author == ctx.me or m.content.startswith(ctx.prefix)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        spammers = Counter(m.author.display_name for m in deleted)
        count = len(deleted)

        messages = [f'{count} message{" was" if count == 1 else "s were"} removed.']
        if len(deleted) > 0:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"– **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=5)


def setup(bot):
    bot.add_cog(Bot(bot))
