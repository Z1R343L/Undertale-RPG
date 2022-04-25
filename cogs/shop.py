import asyncio

import disnake
from disnake.ext import commands, tasks, components

from disnake import ButtonStyle
from disnake.ui import Button, ActionRow
import utility.loader as loader
from utility.dataIO import fileIO
from utility import utils
import time

class FightReturn(disnake.ui.View):
    def __init__(self, bot, author):
        super().__init__()
        self.bot = bot
        self.author = author
        
        
        
    @disnake.ui.button(label="Return to fight")
    async def return_to(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author.id:
            await inter.send("this is not your's kiddo!", ephemeral=True)
            return
        
        button.disabled = True
        await inter.response.edit_message(view=self)
        await self.bot.fights[str(inter.author.id)].menu()
        

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_task.start()

    async def weapon(self, inter, item):
        data = await self.bot.players.find_one({"_id": inter.author.id})
        data["inventory"].remove(item)
        data["inventory"].append(data["weapon"])
        data = {
            "weapon": item,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
        return await inter.send(f"Successfully equipped {item.title()}")

    async def armor(self, inter, item):
        data = await self.bot.players.find_one({"_id": inter.author.id})
        data["inventory"].remove(item)
        data["inventory"].append(data["armor"])

        data = {
            "armor": item,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
        return await inter.send(f"Successfully equipped {item.title()}")

    async def food(self, inter, item):
        data = await self.bot.players.find_one({"_id": inter.author.id})
        data["inventory"].remove(item)
        heal = self.bot.items[item]["HP"]
        data["health"] += heal

        if data["health"] >= data["max_health"]:
            data["health"] = data["max_health"]
            data = {
                "health": data["max_health"],
                "inventory": data["inventory"]
            }
            await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await inter.send("Your health maxed out")
            return
        health = data["health"]
        data = {
            "health": health,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
        return await inter.send(
            f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
        )

    @tasks.loop(seconds=5)
    async def data_task(self):
        self.bot.items = fileIO("data/items/items.json", "load")
        self.bot.monsters = fileIO("data/stats/monsters.json", "load")
        self.bot.locations = fileIO("data/traveling.json", "load")
        self.bot.crates = fileIO("data/crates.json", "load")
        self.bot.boosters = await self.bot.db["boosters"].find_one({"_id": 0})

    @commands.command()
    async def sell(self, inter):
        if str(inter.author.id) in inter.bot.fights:
            tm = inter.bot.fights[str(inter.author.id)].time
            curr_time = time.time()
            delta = int(curr_time) - tm
            if delta >= 1800:
                buttn = FightReturn(bot=self.bot, author=inter.author)
                return await inter.send("You have been in a fight for quite a while right now, Wanna finish this fight?", view=buttn)
            await inter.send(inter.author.mention + " You're in a fight, You cannot use that!")
            return
        author = inter.author
        await loader.create_player_info(inter, inter.author)
        info = await self.bot.players.find_one({"_id": author.id})
        if inter.author.id in inter.bot.fights:
            return
        items = [key for key in info["inventory"]]
        if not items:
            await inter.send("You don't have anything to sell!")
            return

        def countoccurrences(stored, value):
            try:
                stored[value] = stored[value] + 1
            except KeyError:
                stored[value] = 1
                return

        embed = disnake.Embed(
            title="Shop",
            description="Welcome to the shop, selling!",
            color=disnake.Colour.random(),
        )

        rows = []
        lista = []
        inventory = []
        store = {}
        for data in info["inventory"]:
            countoccurrences(store, data)
        for k, v in store.items():
            inventory.append({f"{k}": f"{v}x"})
        for item in inventory:
            for key in item:
                price = self.bot.items[key]["price"]
                lista.append(
                    Button(
                        label=f"{key.title()} {item[key]} | {price / 2}",
                        custom_id=self.s_selected.build_custom_id(item=key.lower(), uid=inter.author.id),
                        style=ButtonStyle.grey,
                    )
                )

        for i in range(0, len(lista), 5):
            rows.append(ActionRow(*lista[i: i + 5]))

        await inter.send(embed=embed, components=rows)

    @components.component_listener()
    async def s_selected(self, inter: disnake.MessageInteraction, item: str, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        info = await self.bot.players.find_one({"_id": inter.author.id})

        returned = self.bot.items[item]["price"] / 2

        info["inventory"].remove(item)

        info["gold"] = info["gold"] + returned

        output = {
            "gold": info["gold"],
            "inventory": info["inventory"]
        }
        await inter.response.defer()

        await self.bot.players.update_one({"_id": inter.author.id}, {"$set": output})

        await inter.send(f"You sold {item} for {round(returned, 1)} G", ephemeral=True)

        msg = await inter.original_message()
        row = await utils.disable_all(msg)

        await inter.edit_original_message(components=row)

    @components.component_listener()
    async def shutdown(self, inter: disnake.MessageInteraction, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()

        msg = await inter.original_message()
        row = await utils.disable_all(msg)

        await inter.edit_original_message(components=row)

    @commands.command()
    async def shop(self, inter):
        if str(inter.author.id) in inter.bot.fights:
            tm = inter.bot.fights[str(inter.author.id)].time
            curr_time = time.time()
            delta = int(curr_time) - tm
            if delta >= 1800:
                buttn = FightReturn(bot=self.bot, author=inter.author)
                return await inter.send("You have been in a fight for quite a while right now, Wanna finish this fight?", view=buttn)
            await inter.send(inter.author.mention + " You're in a fight, You cannot use that!")
            return
        await loader.create_player_info(inter, inter.author)
        data = await inter.bot.players.find_one({"_id": inter.author.id})
        if len(data["inventory"]) >= 10:
            await inter.send("You're carrying alot of items!")
            return
        if inter.author.id in inter.bot.fights:
            return
        items_list = []
        gold = data["gold"]
        for i in self.bot.items:
            if self.bot.items[i]["location"] == data["location"]:
                items_list.append(i)

        embed = disnake.Embed(
            title="Shop",
            description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
            color=disnake.Colour.random(),
        )
        rows = []
        lista = []
        for item in items_list:
            price = self.bot.items[item]["price"]
            if price > data["gold"]:
                lista.append(
                    Button(
                        label=f"{item.title()} | {price} G",
                        style=ButtonStyle.red,
                        disabled=True
                    )
                )
            else:
                lista.append(
                    Button(
                        label=f"{item.title()} | {price} G",
                        custom_id=self.selected.build_custom_id(
                            item=item.lower(),
                            uid=inter.author.id
                        ),
                        style=ButtonStyle.grey
                    )
                )
        lista.append(
            Button(
                label="End Interaction",
                custom_id=self.shutdown.build_custom_id(uid=str(inter.author.id)),
                style=ButtonStyle.red)
        )

        for i in range(0, len(lista), 5):
            rows.append(ActionRow(*lista[i: i + 5]))
        await inter.send(embed=embed, components=rows)

    @components.component_listener()
    async def selected(self, inter: disnake.MessageInteraction, item: str, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return
        incoming = await inter.bot.players.find_one({"_id": inter.author.id})
        gold = incoming["gold"]
        price = self.bot.items[item]["price"]
        embed = disnake.Embed(
            title="Shop",
            description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
            color=disnake.Colour.random(),
        )
        await inter.response.defer()
        if incoming["gold"] < price:
            if "```diff\n- You're gold is not enough\n```" not in embed.description:
                embed.description += "```diff\n- You're gold is not enough\n```"
                await inter.edit_original_message(embed=embed)
            return
        if len(incoming["inventory"]) >= 10:
            if "```diff\n- You're carrying alot of items!\n```" not in embed.description:
                embed.description += "```diff\n- You're carrying alot of items!\n```"
            await inter.edit_original_message(embed=embed)
            return
        incoming["gold"] -= price
        gold = incoming["gold"]
        incoming["inventory"].append(item)

        incoming = {
            "inventory": incoming["inventory"],
            "gold": incoming["gold"]
        }
        await self.bot.players.update_one(
            {"_id": inter.author.id}, {"$set": incoming}
        )
        emb = disnake.Embed(
            title="Shop",
            description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
            color=disnake.Colour.random(),
        )
        embed.description += f"```diff\n+ Successfully bought {item}```"
        await inter.edit_original_message(embed=emb)
        await inter.send(f"Successfully bought **{item}**", ephemeral=True)



    @commands.command()
    async def use(self, inter, *, item: str = None):
        if str(inter.author.id) in inter.bot.fights:
            tm = inter.bot.fights[str(inter.author.id)].time
            curr_time = time.time()
            delta = int(curr_time) - tm
            if delta >= 1800:
                buttn = FightReturn(bot=self.bot, author=inter.author)
                return await inter.send("You have been in a fight for quite a while right now, Wanna finish this fight?", view=buttn)
            await inter.send(inter.author.mention + " You're in a fight, You cannot use that!")
            return
        def countoccurrences(stored, value):
            try:
                stored[value] = stored[value] + 1
            except KeyError:
                stored[value] = 1
                return

        await loader.create_player_info(inter, inter.author)
        if item is None:
            data = await inter.bot.players.find_one({"_id": inter.author.id})
            if len(data["inventory"]) == 0:
                return await inter.send("You have nothing to use")
            items_list = []
            for i in data["inventory"]:
                items_list.append(i)

            embed = disnake.Embed(
                title="Inventory",
                description="Welcome to your Inventory!",
                color=disnake.Colour.random(),
            )

            rows = []
            lista = []
            inventory = []
            store = {}
            for data in data["inventory"]:
                countoccurrences(store, data)

            for k, v in store.items():
                inventory.append({f"{k}": f"{v}x"})

            for item in inventory:
                for key in item:
                    lista.append(
                        Button(
                            label=f"{key.title()} {item[key]}",
                            custom_id=self.u_selected.build_custom_id(
                            item=key.lower(),
                            uid=inter.author.id
                        ),
                            style=ButtonStyle.grey,
                        )
                    )

            for i in range(0, len(lista), 5):
                rows.append(ActionRow(*lista[i: i + 5]))

            await inter.send(embed=embed, components=rows)
            return

        item = item.lower()
        if item not in self.bot.items:
            await inter.send("This item does not exist")
            return

        data = await inter.bot.players.find_one({"_id": inter.author.id})

        if len(data["inventory"]) == 0:
            await inter.send("Your inventory is empty!")
            return

        if item not in data["inventory"]:
            await inter.send("You don't have this item in your inventory!")
            return

        await getattr(Shop, self.bot.items[item]["func"])(self, inter, item)

    @components.component_listener()
    async def u_selected(self, inter: disnake.MessageInteraction, item: str, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()
        msg = await inter.original_message()
        new = await utils.disable_all(msg)
        await inter.edit_original_message(components=[new])
        await getattr(Shop, self.bot.items[item]["func"])(self, inter, item)

    @commands.command()
    async def open(self, inter):
        await loader.create_player_info(inter, inter.author)
        data = await inter.bot.players.find_one({"_id": inter.author.id})
        standard = data["standard crate"]
        determin = data["determination crate"]
        soul = data["soul crate"]
        void = data["void crate"]
        embed = disnake.Embed(
            title="Your boxes",
            description="You can earn boxes by fighting, voting or defeating specific bosses",
            color=disnake.Colour.blue(),
        )
        embed.add_field(
            name="Your boxes",
            value=f"""
Standard crates: {standard}
Determination crates: {determin}
soul crates: {soul}
void crates: {void}
                              """,
        )
        row = ActionRow(
            Button(
                style=ButtonStyle.grey,
                label="Standard Crate",
                custom_id=self.c_selected.build_custom_id(
                            item="standard crate",
                            uid=inter.author.id
                        ),
            ),
            Button(
                style=ButtonStyle.grey,
                label="Determination Crate",
                custom_id=self.c_selected.build_custom_id(
                            item="determination crate",
                            uid=inter.author.id
                        ),
            ),
            Button(
                style=ButtonStyle.grey,
                label="Soul Crate",
                custom_id=self.c_selected.build_custom_id(
                            item="soul crate",
                            uid=inter.author.id
                        ),
            ),
            Button(
                style=ButtonStyle.grey,
                label="Void Crate",
                custom_id=self.c_selected.build_custom_id(
                            item="void crate",
                            uid=inter.author.id
                        ),
            ),
        )
        await inter.send(embed=embed, components=[row])

    @components.component_listener()
    async def c_selected(self, inter: disnake.MessageInteraction, item: str, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        data = await inter.bot.players.find_one({"_id": inter.author.id})
        await inter.response.defer()

        if data[item] == 0:
            return await inter.edit_original_message(
                content=f"You don't have any {item.title()}",
                embed=None,
                components=[],
            )

        await inter.edit_original_message(
            content=f"{inter.author.mention} opened a {item.title()}...",
            embed=None,
            components=[],
        )
        data[item] -= 1
        earned_gold = inter.bot.crates[item]["gold"] + data["level"]
        gold = data["gold"] + earned_gold
        await asyncio.sleep(3)
        await inter.edit_original_message(
            content=f"{inter.author.mention} earned {earned_gold}G from a {item.title()}"
        )
        info = {
            "gold": gold,
            item: data[item]
        }
        return await inter.bot.players.update_one(
            {"_id": inter.author.id}, {"$set": info}
        )

def setup(bot):
    bot.add_cog(Shop(bot))
