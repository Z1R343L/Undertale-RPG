import asyncio
import importlib


from disnake.ext import commands, components
import disnake
from disnake.ui import Button, ActionRow
from disnake import ButtonStyle

import utility.loader as core
import utility.loader as loader
import utility.utils
from utility.dataIO import fileIO

importlib.reload(core)


class Traveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def travel(self, inter):
        """Travel to other spots of the world"""
        if inter.author.id in inter.bot.fights:
            return
        await loader.create_player_info(inter, inter.author)
        info = await self.bot.players.find_one({"_id": inter.author.id})
        data = fileIO("data/traveling.json", "load")
        lista = []

        for key in data:
            if data[key]["RQ_LV"] > info["level"]:
                level = data[key]["RQ_LV"]
                lista.append(
                    Button(label=f"{key.title()} (LV {level})",
                           style=ButtonStyle.grey,
                           disabled=True
                           )
                )
                continue
            lista.append(Button(label=key.title(), custom_id=f"travel:{key}:{inter.author.id}", style=ButtonStyle.blurple, disabled=False))

        rows = []
        for i in range(0, len(lista), 5):
            rows.append(ActionRow(*lista[i: i + 5]))

        em = disnake.Embed(
            title="Where would you like to go?", color=disnake.Color.blue()
        )
        lvl = info["level"]
        loc = info["location"]
        em.description = f"Your Level is **{lvl}**"
        em.description += f"\nYour current location is **{loc.title()}**"
        await inter.send(embed=em, components=rows)



    @components.button_with_id(regex=r"travel:(?P<place>\D+):(?P<uid>\d+)")
    async def selected(self, inter: disnake.MessageInteraction, place: str, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        info = await self.bot.players.find_one({"_id": inter.author.id})
        data = fileIO("data/traveling.json", "load")
        answer = place
        await inter.response.defer()

        if answer == info["location"]:
            await inter.send(f"You are Already At {answer}.")
            return

        if answer in data:
            info["location"] = answer
            out = {
                "location": answer
            }
            await self.bot.players.update_one(
                {"_id": inter.author.id}, {"$set": out}
            )
            em = disnake.Embed(
                description=f"**{inter.author.name}\n\nYou have arrived {answer}**",
                color = disnake.Color.red(),
            )
            msg = await inter.original_message()
            comps = await utility.utils.disable_all(msg)
            await inter.edit_original_message(components=comps)

            return await inter.send(embed=em)


def setup(bot):
    bot.add_cog(Traveling(bot))
