import asyncio

import discord
from discord.ext import commands, tasks
from dislash import *

import botTools.loader as loader
from botTools.dataIO import fileIO


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_task.start()

    async def weapon(self, ctx, item):
        data = await self.bot.players.find_one({"_id": ctx.author.id})
        data["inventory"].remove(item)
        data["inventory"].append(data["weapon"])
        data = {
            "weapon": item,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
        return await ctx.send(f"Successfully equipped {item.title()}")

    async def armor(self, ctx, item):
        data = await self.bot.players.find_one({"_id": ctx.author.id})
        print(item)
        data["inventory"].remove(item)
        data["inventory"].append(data["armor"])

        data = {
            "armor": item,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
        return await ctx.send(f"Successfully equipped {item.title()}")

    async def food(self, ctx, item):
        data = await self.bot.players.find_one({"_id": ctx.author.id})
        data["inventory"].remove(item)
        heal = self.bot.items[item]["HP"]
        data["health"] += heal

        if data["health"] >= data["max_health"]:
            data["health"] = data["max_health"]
            data = {
                "health": data["max_health"],
                "inventory": data["inventory"]
            }
            await self.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
            await ctx.send("Your health maxed out")
            return
        health = data["health"]
        data = {
            "health": health,
            "inventory": data["inventory"]
        }
        await self.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
        return await ctx.send(
            f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
        )

    @tasks.loop(seconds=5)
    async def data_task(self):
        self.bot.items = fileIO("data/items/items.json", "load")
        self.bot.monsters = fileIO("data/stats/monsters.json", "load")
        self.bot.locations = fileIO("data/traveling.json", "load")
        self.bot.crates = fileIO("data/crates.json", "load")
        self.bot.boosters = await self.bot.db["boosters"].find_one({"_id": 0})

    @commands.command(alaises=["sellshop", "s"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def sell(self, ctx):
        author = ctx.author
        await loader.create_player_info(ctx, ctx.author)
        info = await self.bot.players.find_one({"_id": author.id})
        if info["fighting"]:
            return
        items = [key for key in info["inventory"]]
        if not items:
            await ctx.send("You don't have anything to sell!")
            ctx.command.reset_cooldown(ctx)
            return

        def countoccurrences(stored, value):
            try:
                stored[value] = stored[value] + 1
            except KeyError:
                stored[value] = 1
                return

        embed = discord.Embed(
            title="Shop",
            description="Welcome to the shop, selling!",
            color=discord.Colour.random(),
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
                        custom_id=key,
                        style=ButtonStyle.grey,
                    )
                )

        for i in range(0, len(lista), 5):
            rows.append(ActionRow(*lista[i: i + 5]))

        msg = await ctx.send(embed=embed, components=rows)

        on_click = msg.create_click_listener(timeout=30)

        @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.from_user(ctx.author)
        async def selected(inter):
            on_click.kill()
            await msg.edit(components=[])
            answer = inter.component.custom_id
            returned = self.bot.items[answer]["price"] / 2

            info["inventory"].remove(answer)

            info["gold"] = info["gold"] + returned

            output = {
                "gold": info["gold"],
                "inventory": info["inventory"]
            }

            await self.bot.players.update_one({"_id": author.id}, {"$set": output})

            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"You sold {answer} for {round(returned, 1)} G")

    @commands.command(aliases=["buy"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def shop(self, ctx, *, item: str = None):
        await loader.create_player_info(ctx, ctx.author)
        if item is None:
            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            if len(data["inventory"]) >= 10:
                await ctx.send("Your carrying alot of items!")
                return
            if data["fighting"]:
                return
            items_list = []
            gold = data["gold"]
            for i in self.bot.items:
                if self.bot.items[i]["location"] == data["location"]:
                    items_list.append(i)

            embed = discord.Embed(
                title="Shop",
                description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
                color=discord.Colour.random(),
            )
            rows = []
            lista = []
            for item in items_list:
                price = self.bot.items[item]["price"]
                lista.append(
                    Button(label=f"{item.title()} | {price} G", custom_id=item, style=ButtonStyle.grey)
                )
            lista.append(
                Button(label="⛔", custom_id="shut", style=ButtonStyle.red))

            for i in range(0, len(lista), 5):
                rows.append(ActionRow(*lista[i: i + 5]))
            msg = await ctx.send(embed=embed, components=rows)

            on_click = msg.create_click_listener(timeout=300)

            @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
            async def on_wrong_user(inter):
                await inter.reply("This is not yours kiddo!", ephemeral=True)

            @on_click.matching_id("shut")
            async def shutdown(inter):
                for b in rows:
                    b.disable_buttons()
                await msg.edit(components=rows)
                on_click.kill()
                await inter.reply("Closed store", ephemeral=True)
                return

            @on_click.from_user(ctx.author)
            async def selected(inter):
                if inter.component.custom_id == "shut":
                    return

                incoming = await ctx.bot.players.find_one({"_id": ctx.author.id})
                gold = incoming["gold"]
                price = self.bot.items[inter.component.custom_id]["price"]
                embed = discord.Embed(
                    title="Shop",
                    description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
                    color=discord.Colour.random(),
                )
                if incoming["gold"] < price:
                    if "```diff\n- Your gold is not enough\n```" not in embed.description:
                        embed.description += "```diff\n- Your gold is not enough\n```"
                        await msg.edit(embed=embed)
                    return
                if len(incoming["inventory"]) >= 10:
                    if "```diff\n- Your carrying alot of items!\n```" not in embed.description:
                        embed.description += "```diff\n- Your carrying alot of items!\n```"
                    await msg.edit(embed=embed)
                    return
                incoming["gold"] -= price
                gold = incoming["gold"]
                incoming["inventory"].append(inter.component.custom_id)

                incoming = {
                    "inventory": incoming["inventory"],
                    "gold": incoming["gold"]
                }
                await self.bot.players.update_one(
                    {"_id": ctx.author.id}, {"$set": incoming}
                )
                emb = discord.Embed(
                    title="Shop",
                    description=f"Welcome to the shop!\nYour gold: **{int(gold)}**",
                    color=discord.Colour.random(),
                )
                embed.description += f"```diff\n+ Successfully bought {inter.component.custom_id}```"
                await msg.edit(embed=emb)
                await inter.reply(f"Successfully bought **{inter.component.custom_id}**", ephemeral=True)

            return
        item = item.lower()
        if item not in self.bot.items:
            await ctx.send("this item does not exist")
            return
        data = await ctx.bot.players.find_one({"_id": ctx.author.id})
        if len(data["inventory"]) >= 10:
            await ctx.send("Your carrying alot of items!")
            return
        if self.bot.items[item]["location"] != data["location"]:
            await ctx.send("this item does not exist in your location")
            return
        price = self.bot.items[item]["price"]
        if data["gold"] < price:
            await ctx.send("Your gold is not enough")
            return
        data["gold"] -= price
        data["inventory"].append(item)

        await self.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f"Successfully bought {item}")

    @commands.command(aliases=["consume", "heal", "equip"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def use(self, ctx, *, item: str = None):
        def countoccurrences(stored, value):
            try:
                stored[value] = stored[value] + 1
            except KeyError:
                stored[value] = 1
                return

        await loader.create_player_info(ctx, ctx.author)
        if item is None:
            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            if len(data["inventory"]) == 0:
                return await ctx.send("You have nothing to use")
            items_list = []
            for i in data["inventory"]:
                items_list.append(i)

            embed = discord.Embed(
                title="Inventory",
                description="Welcome to your Inventory!",
                color=discord.Colour.random(),
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
                            custom_id=key.lower(),
                            style=ButtonStyle.grey,
                        )
                    )

            for i in range(0, len(lista), 5):
                rows.append(ActionRow(*lista[i: i + 5]))

            msg = await ctx.send(embed=embed, components=rows)

            on_click = msg.create_click_listener(timeout=120)

            @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
            async def on_wrong_user(inter):
                await inter.reply("This is not yours kiddo!", ephemeral=True)

            @on_click.from_user(ctx.author)
            async def selected(inter):
                on_click.kill()
                selected_item = inter.component.custom_id
                await msg.edit(components=[])
                ctx.command.reset_cooldown(ctx)
                await getattr(Shop, self.bot.items[selected_item]["func"])(self, ctx, selected_item)

            return

        item = item.lower()
        if item not in self.bot.items:
            await ctx.send("This item does not exist")
            ctx.command.reset_cooldown(ctx)
            return

        data = await ctx.bot.players.find_one({"_id": ctx.author.id})

        if len(data["inventory"]) == 0:
            await ctx.send("Your inventory is empty!")
            ctx.command.reset_cooldown(ctx)
            return

        if item not in data["inventory"]:
            await ctx.send("You don't have this item in your inventory!")
            ctx.command.reset_cooldown(ctx)
            return

        await getattr(Shop, self.bot.items[item]["func"])(self, ctx, item)

    @commands.command(aliases=["opencrate", "open_crate", "crate"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def open(self, ctx):
        await loader.create_player_info(ctx, ctx.author)
        data = await ctx.bot.players.find_one({"_id": ctx.author.id})
        standard = data["standard crate"]
        determin = data["determination crate"]
        soul = data["soul crate"]
        void = data["void crate"]
        embed = discord.Embed(
            title="Your boxes",
            description="You can earn boxes by fighting, voting or defeating specific bosses",
            color=discord.Colour.blue(),
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
            Button(style=ButtonStyle.grey, label="Standard Crate", custom_id="standard crate"),
            Button(
                style=ButtonStyle.grey, label="Determination Crate", custom_id="determination crate"
            ),
            Button(style=ButtonStyle.grey, label="Soul Crate", custom_id="soul crate"),
            Button(style=ButtonStyle.grey, label="Void Crate", custom_id="void crate"),
        )
        msg = await ctx.send(embed=embed, components=[row])

        on_click = msg.create_click_listener(timeout=30)

        @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.from_user(ctx.author)
        async def selected(inter):
            on_click.kill()
            item = inter.component.custom_id
            if data[item] == 0:
                ctx.command.reset_cooldown(ctx)
                return await msg.edit(
                    content=f"You don't have any {item.title()}",
                    embed=None,
                    components=[],
                )

            await msg.edit(
                content=f"{ctx.author.mention} opened a {item.title()}...",
                embed=None,
                components=[],
            )
            data[item] -= 1
            gold = ctx.bot.crates[item]["gold"] + data["level"]
            data["gold"] += gold
            await asyncio.sleep(3)
            await msg.edit(
                content=f"{ctx.author.mention} earned {gold}G from a {item.title()}"
            )
            ctx.command.reset_cooldown(ctx)
            info = {
                "gold": gold,
                item: data[item]
            }
            return await ctx.bot.players.update_one(
                {"_id": ctx.author.id}, {"$set": info}
            )


def setup(bot):
    bot.add_cog(Shop(bot))
