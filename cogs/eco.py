import importlib
import random
import time

import discord
from discord.ext import commands

import botTools.loader as loader
import cogs.fighting as fighting

importlib.reload(loader)

starttime = time.time()


class Economy(commands.Cog):
    """Economy module and balance related"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reset(self, ctx):
        await loader.create_player_info(ctx, ctx.author)
        old_data = await self.bot.players.find_one({"_id": ctx.author.id})

        if old_data["level"] < 70:
            await ctx.send(
                "you are not yet passed, reach **LVL70**, and you shall come back"
            )
            return

        await ctx.send(
            "Are you sure you want to proceed!\n\nYou will gain the ability to travel other dimension, and your gold and xp will be doubled each time you get some\n\n**Yes**\t\t\t\t**No**"
        )
        answer = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            timeout=60,
        )
        if answer.content.lower() == "yes":
            await self.bot.players.delete_one({"_id": ctx.author.id})
            await loader.create_player_info(ctx, ctx.author)
            new_data = await self.bot.players.find_one({"_id": ctx.author.id})
            new_data["resets"] = old_data["resets"] + 1
            new_data["multi_g"] = old_data["multi_g"] + 0.7
            new_data["multi_xp"] = old_data["multi_xp"] + 0.4
            new_data["tokens"] = old_data["tokens"]
            await self.bot.players.update_one(
                {"_id": ctx.author.id}, {"$set": new_data}
            )
            await ctx.send("You have rested your world.")
        else:
            await ctx.send("You shall come back again!")

    @commands.command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def daily(self, ctx):
        """Claim Your daily Reward!"""
        author = ctx.author
        await loader.create_player_info(ctx, ctx.author)

        info = await self.bot.players.find_one({"_id": author.id})
        goldget = 500 * info["multi_g"]
        curr_time = time.time()
        delta = int(curr_time) - int(info["daily_block"])

        if delta >= 86400 and delta > 0:
            info["gold"] += goldget
            info["daily_block"] = curr_time
            await self.bot.players.update_one({"_id": author.id}, {"$set": info})
            em = discord.Embed(
                description=f"**You received your daily gold! {int(goldget)} G**",
                color=discord.Color.blue(),
            )
        else:
            seconds = 86400 - delta
            em = discord.Embed(
                description=f"**You can't claim your daily reward yet!\n\nYou can claim your daily reward <t:{int(time.time()) + int(seconds)}:R>**",
                color=discord.Color.red(),
            )

        await ctx.send(embed=em)

    @commands.command(aliases=["bal", "balance"])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def gold(self, ctx):
        """Check your gold balance"""
        await loader.create_player_info(ctx, ctx.author)
        info = await self.bot.players.find_one({"_id": ctx.author.id})
        bal = info["gold"]
        embed = discord.Embed(
            title="Balance",
            description=f"Your balance:\n**{int(bal)}G**",
            color=discord.Colour.random(),
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["level", "progress", "lvl", "stat", "profile"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(self, ctx, member: discord.User = None):
        """Check your stats and powers"""
        player = member or ctx.author
        await loader.create_player_info(ctx, ctx.author)
        info = await self.bot.players.find_one({"_id": player.id})
        max_xp = 100 * info["level"]
        xp = info["exp"]
        # stats
        level = info["level"]
        health = info["health"]
        max_health = info["max_health"]

        bar = await fighting.get_bar(health, max_health)
        attack = info["damage"]
        armor = info["armor"]
        weapon = info["weapon"]
        deaths = info["deaths"]
        gold = info["gold"]
        kills = info["kills"]
        resets = info["resets"]
        g_mult = info["multi_g"]
        xp_mult = info["multi_xp"]
        tokens = info["tokens"]

        embed = discord.Embed(
            title=f"{player.name}‘s Stats!",
            description="Your Status and progress in the game",
            color=discord.Color.random(),
        )
        embed.add_field(
            name="<:HP:916553886339309588>┃Health",
            value=f"{health}/{max_health} {bar}"
        )
        embed.add_field(
            name="<:LV:916554742975590450>┃LOVE",
            value=f"{level}"
        )
        embed.add_field(
            name="<:XP:916555463145971772>┃XP",
            value=f"{round(xp)}/{max_xp}"
        )
        embed.add_field(
            name="<:KillsWeapon:916556418025414657> ┃kills",
            value=f"{kills}"
        )
        embed.add_field(
            name="<:broken_heart:865088299520753704>┃deaths",
            value=f"{deaths}"
        )
        embed.add_field(
            name="<:KillsWeapon:916556418025414657> ┃Weapon",
            value=f"{weapon}"
        )
        embed.add_field(
            name="<:armor:916558817595097098>┃Armor",
            value=f"{armor}"
        )
        embed.add_field(
            name="<:fist:916558332280598528>┃Attack",
            value=f"{attack}"
        )
        embed.add_field(
            name="<:gold:924599104674332727>┃Gold",
            value=f"{int(gold)}"
        )
        embed.add_field(name="▫️┃Tokens", value=f"{int(tokens)}")
        embed.add_field(name="▫️┃Resets", value=f"{resets}")
        embed.add_field(name="▫️┃Gold Multiplier", value=f"{round(g_mult, 1)}x")
        embed.add_field(name="▫️┃XP Multiplier", value=f"{round(xp_mult, 1)}x")

        embed.set_thumbnail(url=player.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        """Shows your inventory"""
        author = ctx.author
        await loader.create_player_info(ctx, ctx.author)
        info = await self.bot.players.find_one({"_id": author.id})

        def countoccurrences(stored, value):
            try:
                stored[value] = stored[value] + 1
            except KeyError:
                stored[value] = 1
                return

        gold = info["gold"]

        # func
        store = {}
        inventory = ""
        for data in info["inventory"]:
            countoccurrences(store, data)
        for k, v in store.items():
            inventory += f"{k} {v}x\n"

        em = discord.Embed(title="Your Inventory", color=discord.Colour.random())
        em.add_field(name="▫️┃Gold:", value=f"**{int(gold)}**", inline=False)
        em.add_field(name="📦┃Items:", value=f"**{inventory}**", inline=False)
        em.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send(embed=em)

    @commands.command(aliases=["sp"])
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def supporter(self, ctx):
        """Join our support server and claim a bunch of gold"""
        await loader.create_player_info(ctx, ctx.author)
        while True:
            if ctx.guild.id != 817437132397871135:
                await ctx.send(
                    "this command is exclusive for our server, you can join via \n\n https://discord.gg/FQYVpuNz4Q"
                )
                return
            author = ctx.author

            info = await self.bot.players.find_one({"_id": author.id})
            goldget = random.randint(500, 1000) * info["multi_g"]
            try:
                curr_time = time.time()
                delta = int(curr_time) - int(info["supporter_block"])

                if delta >= 86400 and delta > 0:
                    info["gold"] += goldget
                    info["supporter_block"] = curr_time
                    await self.bot.players.update_one(
                        {"_id": author.id}, {"$set": info}
                    )
                    em = discord.Embed(
                        description=f"**You received your supporter gold! {int(goldget)} G**",
                        color=discord.Color.blue(),
                    )
                else:
                    seconds = 86400 - delta
                    em = discord.Embed(
                        description=f"**You can't claim your supporter reward yet!\n\n You can use this command again <t:{int(time.time()) + int(seconds)}:R>**",
                        color=discord.Color.red(),
                    )
                await ctx.send(embed=em)
                break
            except KeyError:
                info["supporter_block"] = 0
                await self.bot.players.update_one({"_id": author.id}, {"$set": info})
                continue


def setup(bot):
    bot.add_cog(Economy(bot))
