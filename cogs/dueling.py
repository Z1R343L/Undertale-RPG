import asyncio
import importlib
import random

import discord
from discord.ext import commands
from dislash import *

import botTools.loader as loader

importlib.reload(loader)


class Duel(commands.Cog):
    def __init_(self, bot):
        self.bot = bot

    @commands.command(aliases=[])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def duel(self, ctx, p2: discord.Member = None):
        p1 = ctx.author
        if p2 is None:
            await ctx.send("You should mention a user to duel with!")
            return

        if p1 == p2:
            return await ctx.send("Nice try ;)")

        if p2.bot:
            return await ctx.send("Nice try ;)")

        await loader.create_player_info(ctx, p1)
        await loader.create_player_info(ctx, p2)

        p1_dat = await ctx.bot.players.find_one({"_id": p1.id})
        p2_dat = await ctx.bot.players.find_one({"_id": p2.id})

        if p1_dat["fighting"] or p2_dat["fighting"]:
            await ctx.send(
                "One of you is already on a fight, please continue it and execute this command again!"
            )
            return
        p1_health = p1_dat["health"]
        p2_health = p2_dat["health"]
        embed = discord.Embed(
            title=f"{ctx.author.name} Requests a fight!",
            description=f"Your HP is {p2_health}",
            color=discord.Color.blue(),
        )
        embed.set_author(name=f"Fight! {p1.name}'s HP is {p1_health}")
        embed.set_thumbnail(url=p1.avatar_url)

        row = ActionRow(
            Button(style=ButtonStyle.green, label="Yes", custom_id="yes"),
            Button(style=ButtonStyle.red, label="No", custom_id="no"),
        )

        msg = await ctx.send(p2.mention, embed=embed, components=[row])

        on_click = msg.create_click_listener(timeout=120)

        @on_click.not_from_user(p2, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.matching_id("no")
        async def on_test_button(inter, reset_timeout=False):
            embed.description += "\n\n**You Flee'd**"
            await msg.edit(embed=embed, components=[])
            on_click.kill()

        @on_click.matching_id("yes")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[])
            on_click.kill()
            p1_dat["fighting"] = False
            p2_dat["fighting"] = False
            await ctx.bot.players.update_one({"_id": p1.id}, {"$set": p1_dat})
            await ctx.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
            await Menu.menu(self, ctx, p1, p2)


def setup(bot):
    bot.add_cog(Duel(bot))


class Core:
    async def get_xp_bar(xp, max_xp):
        bar0 = "<:0_:877147611096842271>"
        bar1 = "<:1_:877147647880880169> "
        bar2 = "<:2_:877147680638382080>"
        bar4 = "<:4_:877147771159842836>"
        bar5 = "<:5_:877147798619959296>"
        bar = None
        mix = xp / max_xp
        per = mix * 100
        if per == 0:
            bar = f"{bar0}{bar0}{bar0}{bar0}{bar0}"
        if per <= 10 and per > 0:
            bar = f"{bar2}{bar0}{bar0}{bar0}{bar0}"
        if 20 >= per > 10:
            bar = f"{bar5}{bar0}{bar0}{bar0}{bar0}"
        if 30 >= per > 20:
            bar = f"{bar5}{bar2}{bar0}{bar0}{bar0}"
        if 40 >= per > 30:
            bar = f"{bar5}{bar4}{bar0}{bar0}{bar0}"
        if 50 >= per > 40:
            bar = f"{bar5}{bar5}{bar2}{bar0}{bar0}"
        if 60 >= per > 50:
            bar = f"{bar5}{bar5}{bar4}{bar0}{bar0}"
        if 70 >= per > 60:
            bar = f"{bar5}{bar5}{bar5}<:3_:877147741392871465>{bar0}"
        if 80 >= per > 70:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar2}"
        if 90 >= per > 80:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar4}"
        if per <= 100 and per > 90:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar5}"
        return bar

    async def get_bar(health, max_health):
        bar0 = "<:0_:876786251892654090>"
        bar2 = "<:2_:876786310931681361>"
        bar4 = "<:4_:876786361934413854>"
        bar5 = "<:5_:876786380888494120>"
        bar = None
        mix = health / max_health
        per = mix * 100
        if per == 0:
            bar = f"{bar0}{bar0}{bar0}{bar0}{bar0}"
        if 10 >= per > 0:
            bar = f"{bar2}{bar0}{bar0}{bar0}{bar0}"
        if 20 >= per > 10:
            bar = f"{bar5}{bar0}{bar0}{bar0}{bar0}"
        if per <= 30 and per > 20:
            bar = f"{bar5}{bar2}{bar0}{bar0}{bar0}"
        if 40 >= per > 30:
            bar = f"{bar5}{bar4}{bar0}{bar0}{bar0}"
        if per <= 50 and per > 40:
            bar = f"{bar5}{bar5}{bar2}{bar0}{bar0}"
        if per <= 60 and per > 50:
            bar = f"{bar5}{bar5}{bar4}{bar0}{bar0}"
        if per <= 70 and per > 60:
            bar = f"{bar5}{bar5}{bar5}<:3_:876786332817575946>{bar0}"
        if per <= 80 and per > 70:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar2}"
        if per <= 90 and per > 80:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar4}"
        if per <= 100 and per > 90:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar5}"
        return bar

    async def count(store, value):
        try:
            store[value] = store[value] + 1
        except KeyError as e:
            store[value] = 1
            return


class Menu:
    async def menu(self, ctx, att, rec):
        row = ActionRow(
            Button(style=ButtonStyle.red, label="Fight", custom_id="fight"),
            Button(style=ButtonStyle.gray, label="Items", custom_id="items"),
            Button(style=ButtonStyle.green, label="mercy", custom_id="spare"),
        )

        embed = discord.Embed(title="Choose an Option:", color=discord.Colour.red())
        msg = await ctx.send(att.mention, embed=embed, components=[row])
        on_click = msg.create_click_listener(timeout=120)

        @on_click.not_from_user(att, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.matching_id("fight")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[])
            on_click.kill()
            await Attack.attack(self, ctx, att, rec)

        @on_click.matching_id("items")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[])
            on_click.kill()
            await Items.use(self, ctx, att, rec)

        @on_click.matching_id("spare")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[])
            on_click.kill()
            await Mercy.spare(self, ctx, att, rec)

        @on_click.timeout
        async def on_timeout():
            p1_dat = await ctx.bot.players.find_one({"_id": att.id})
            p2_dat = await ctx.bot.players.find_one({"_id": rec.id})
            p1_dat["fighting"] = False
            p2_dat["fighting"] = False
            await ctx.bot.players.update_one({"_id": att.id}, {"$set": p1_dat})
            await ctx.bot.players.update_one({"_id": rec.id}, {"$set": p2_dat})


class Attack:
    async def attack(self, ctx, p1, p2):
        p1_dat = await ctx.bot.players.find_one({"_id": p1.id})
        p2_dat = await ctx.bot.players.find_one({"_id": p2.id})

        weapon_dat = ctx.bot.items
        armor_dat = ctx.bot.items

        p1_weapon = p1_dat["weapon"]
        p2_weapon = p2_dat["weapon"]

        p1_armor = p1_dat["armor"]
        p2_armor = p2_dat["armor"]

        p1_raw_damage = p1_dat["damage"]
        p2_raw_damage = p2_dat["damage"]

        # calc for player 1 status
        min_dmg = weapon_dat[p1_weapon]["min_dmg"]
        min_dfs = armor_dat[p1_armor]["min_dfs"]
        max_dmg = weapon_dat[p1_weapon]["max_dmg"]
        max_dfs = armor_dat[p1_armor]["max_dfs"]
        p1_dmg = random.randint(min_dmg, max_dmg)
        p1_dfs = random.randint(min_dfs, max_dfs)

        # calc for player 2 status
        min_dmg = weapon_dat[p2_weapon]["min_dmg"]
        min_dfs = armor_dat[p2_armor]["min_dfs"]
        max_dmg = weapon_dat[p2_weapon]["max_dmg"]
        max_dfs = armor_dat[p2_armor]["max_dfs"]
        p2_dmg = random.randint(min_dmg, max_dmg)
        p2_dfs = random.randint(min_dfs, max_dfs)

        p1_hp = p1_dat["health"]
        p2_hp = p2_dat["health"]

        dodge_chance = random.randint(1, 10)

        atem = discord.Embed(title="You Attack")

        if dodge_chance in [5, 9]:
            atem.description = f"**{p2}** Dodged the atack!"
            await ctx.send(p1.mention, embed=atem)
            await asyncio.sleep(3)
            await Menu.menu(self, ctx, p2, p1)
            return
        else:
            # player attack
            enemy_hp_after = int(p2_hp) - int(p1_dmg)
            enemy_hp_after = max(enemy_hp_after, 0)
            atem.description = f"You Damaged **{p2}**\n**-{p1_dmg}HP**\ncurrent emeny hp: **{enemy_hp_after}HP**"

            atem.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
            )
            await ctx.send(p1.mention, embed=atem)
            if enemy_hp_after <= 0:
                await asyncio.sleep(1)
                embed = discord.Embed(title="You Won!", color=discord.Colour.gold())
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/850983850665836544/878997428840329246/image0.png"
                )

                await ctx.send(embed=embed)
                p1_dat["fighting"] = False
                p2_dat["fighting"] = False
                await ctx.bot.players.update_one({"_id": p1.id}, {"$set": p1_dat})
                await ctx.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
                print(f"{p1} and {p2} has ended the fight")
                return

            else:
                p2_dat["health"] = enemy_hp_after
                await ctx.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
                await asyncio.sleep(2)
                await Menu.menu(self, ctx, p2, p1)


class Items:
    async def weapon(self, ctx, p1, p2, item):
        data = await ctx.bot.players.find_one({"_id": p1.id})
        data["inventory"].remove(item)
        data["inventory"].append(data["weapon"])
        data["weapon"] = item
        await ctx.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await ctx.send(f"Successfully equiped {item.title()}")
        await asyncio.sleep(2)
        return await Menu.menu(self, ctx, p2, p1)  # replace

    async def armor(self, ctx, p1, p2, item):
        data = await ctx.bot.players.find_one({"_id": p1.id})
        print(str(item))
        data["inventory"].remove(item)
        data["inventory"].append(data["armor"])

        data["armor"] = item
        await ctx.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await ctx.send(f"Succesfully equiped {item.title()}")
        await asyncio.sleep(2)
        return await Attack.counter_attack(self, ctx)

    async def food(self, ctx, p1, p2, item):
        data = await ctx.bot.players.find_one({"_id": p1.id})
        data["inventory"].remove(item)
        heal = ctx.bot.items[item]["HP"]
        data["health"] += heal

        if data["health"] >= data["max_health"]:
            data["health"] = data["max_health"]
            await ctx.bot.players.update_one({"_id": p1.id}, {"$set": data})
            await ctx.send("Your health maxed out")
            await asyncio.sleep(2)
            return await Menu.menu(self, ctx, p2, p1)  # replace
        health = data["health"]
        await ctx.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await ctx.send(
            f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
        )
        await asyncio.sleep(2)
        return await Menu.menu(self, ctx, p2, p1)  # replace

    async def use(self, ctx, p1, p2):
        def countoccurrences(store, value):
            try:
                store[value] = store[value] + 1
            except KeyError as e:
                store[value] = 1
                return

        await loader.create_player_info(ctx, p1)
        data = await ctx.bot.players.find_one({"_id": p1.id})
        if len(data["inventory"]) == 0:
            await ctx.send("You have nothing to use")
            await asyncio.sleep(2)
            return await Menu.menu(self, ctx, p1, p2)  # replace

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
                        style=2,
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
            item = inter.component.id
            await msg.edit(components=[])
            try:
                await getattr(Items, ctx.bot.items[item]["func"])(self, ctx, p1, p2, item)
            except KeyError:
                await ctx.send("Nothing happened")
                await asyncio.sleep(2)
                return await Menu.menu(self, ctx, p2, p1)  # replace


class Mercy:
    async def spare(self, ctx, p1, p2):
        p1_dat = await ctx.bot.players.find_one({"_id": p1.id})
        p2_dat = await ctx.bot.players.find_one({"_id": p2.id})
        p1_dat["fighting"] = False
        p2_dat["fighting"] = False
        await ctx.bot.players.update_one({"_id": p1.id}, {"$set": p1_dat})
        await ctx.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
        await ctx.send(f"{p2.mention}\n\n{p1} has spared you!, battle is done")
