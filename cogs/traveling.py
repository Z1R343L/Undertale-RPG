import asyncio
import importlib

import discord
from discord.ext import commands
from dislash import *

import botTools.loader as core
import botTools.loader as loader
from botTools.dataIO import fileIO

importlib.reload(core)


class Traveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["tv"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def travel(self, ctx):
        """Travel to other spots of the world"""
        if ctx.author.id in ctx.bot.fights:
            return
        await loader.create_player_info(ctx, ctx.author)
        info = await self.bot.players.find_one({"_id": ctx.author.id})
        data = fileIO("data/traveling.json", "load")
        lista = []

        for key in data:
            if data[key]["RQ_LV"] > info["level"]:
                level = data[key]["RQ_LV"]
                lista.append(Button(label=f"{key.title()} (LV {level})", custom_id=key, style=ButtonStyle.grey, disabled=True))
                continue
            lista.append(Button(label=key.title(), custom_id=key, style=ButtonStyle.blurple, disabled=False))

        rows = []
        for i in range(0, len(lista), 5):
            rows.append(ActionRow(*lista[i: i + 5]))

        em = discord.Embed(
            title="Where would you like to go?", color=discord.Color.blue()
        )
        lvl = info["level"]
        loc = info["location"]
        em.description = f"Your Level is **{lvl}**"
        em.description += f"\nYour current location is **{loc.title()}**"
        msg = await ctx.send(embed=em, components=rows)

        on_click = msg.create_click_listener(timeout=60)

        @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.from_user(ctx.author)
        async def traveling(inter):
            on_click.kill()
            await msg.edit(components=[])
            answer = inter.component.custom_id

            if answer == info["location"]:
                await ctx.send(f"You are Already At {answer}.")
                return

            if answer in data:
                em = discord.Embed(
                    description=f"**{ctx.author.name} Traveling to {answer}...**",
                    color=discord.Color.red(),
                )
                msg_1 = await ctx.send(embed=em)
                await asyncio.sleep(3)
                info["location"] = answer
                out = {
                    "location": answer
                }
                await self.bot.players.update_one(
                    {"_id": ctx.author.id}, {"$set": out}
                )
                em.description = f"**{ctx.author.name}\n\nYou have arrived {answer}**"
                return await msg_1.edit(embed=em)


def setup(bot):
    bot.add_cog(Traveling(bot))
