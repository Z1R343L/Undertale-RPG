import asyncio
import random

import disnake
from disnake.ext import commands, components
from disnake.ui import Button, ActionRow
from disnake.enums import ButtonStyle

from utility.utils import create_player_info, occurrence


class DuelCog(commands.Cog):
    def __init_(self, bot):
        self.bot = bot

    @components.button_listener()
    async def duel_action(self, inter: disnake.MessageInteraction, action: str, uid: int, pl_id: int) -> None:
        if inter.author.id != uid:
            await inter.send('This is not yours kiddo!', ephemeral=True)
            return

        try:
            await inter.response.defer()
        except:
            pass

        await inter.edit_original_message(components=[])

        return await getattr(inter.bot.duels[str(uid)], action)(pl_id)

    @components.button_listener()
    async def duel_accepter(self, inter: disnake.MessageInteraction, choice: str, uid: str):
        if uid != str(inter.author.id):
            return await inter.send("This is not your's kiddo!", ephemeral=True)

        try:
            await inter.response.defer()
        except:
            pass

        if choice == "yes":
            await inter.edit_original_message(components=[])
            await inter.bot.duels[uid].menu(self, inter, 2)
        else:
            await inter.edit_original_message(content="You fleed", components=[])

    @commands.slash_command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def duel(self, inter, p2: disnake.Member = None):
        p1 = inter.author
        if p2 is None:
            await inter.send("You should mention a user to duel with!")
            return

        if p2.bot:
            return await inter.send("Nice try ;)")

        await create_player_info(inter, p1)
        await create_player_info(inter, p2)

        p1_dat = await inter.bot.players.find_one({"_id": p1.id})
        p2_dat = await inter.bot.players.find_one({"_id": p2.id})

        p1_health = p1_dat["health"]
        p2_health = p2_dat["health"]
        embed = disnake.Embed(
            title=f"{inter.author.name} Requests a fight!",
            description=f"Your HP is {p2_health}",
            color=disnake.Color.blue(),
        )
        embed.set_author(name=f"Fight! {p1.name}'s HP is {p1_health}")
        embed.set_thumbnail(url=p1.avatar.url)

        row = ActionRow(
            Button(style=ButtonStyle.green, label="Yes", custom_id=self.duel_accepter.build_custom_id(choice="yes", uid=p2.id)),
            Button(style=ButtonStyle.red, label="No", custom_id=self.duel_accepter.build_custom_id(choice="no", uid=p2.id)),
        )

        duel_obj = Duel(inter.bot, p1, p2, inter)
        inter.bot.duels[str(p2.id)] = duel_obj

        return await inter.send(p2.mention, embed=embed, components=[row])


def setup(bot):
    bot.add_cog(DuelCog(bot))

class Duel:
    def __init__(self, bot, p1, p2, inter):
        self.duelers = [p1, p2]
        self.bot = bot
        self.inter = inter

    async def menu(self, player: int):
        opponent = None

        if player == 1:
            opponent = 2
        else:
            opponent = 1

        buttons = [
            disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                label='Fight',
                custom_id=DuelCog.duel_action.build_custom_id(action="attack", uid=self.author.id, pl_id=player)
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.gray,
                label='Items',
                custom_id=DuelCog.duel_action.build_custom_id(action="use", uid=self.author.id)
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.grey,
                label='Act',
                disabled=True
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label='Mercy',
                custom_id=DuelCog.duel_action.build_custom_id(action="spare", uid=self.author.id)
            ),
        ]

        embed = disnake.Embed(title="Choose an Option:", color=disnake.Colour.red())
        msg = await self.inter.send(self[player].mention, embed=embed, components=[row])

        @on_click.matching_id("fight")
        async def on_test_button():
            await msg.edit(components=[])
            await self.attack(player, opponent)

        @on_click.matching_id("items")
        async def on_test_button():
            await msg.edit(components=[])
            on_click.kill()
            await self.use(player, opponent)

        @on_click.matching_id("spare")
        async def on_test_button():
            await msg.edit(components=[])
            on_click.kill()
            await self.spare(player, opponent)


    async def attack(self, player, opponent):
        p1 = self.duelers[player]
        p2 = self.duelers[opponent]
        p1_dat = await self.inter.bot.players.find_one({"_id": p1.id})
        p2_dat = await self.inter.bot.players.find_one({"_id": p2.id})

        weapon_dat = self.inter.bot.items

        p1_weapon = p1_dat["weapon"]

        # calc for player 1 status
        min_dmg = weapon_dat[p1_weapon]["min_dmg"]
        max_dmg = weapon_dat[p1_weapon]["max_dmg"]
        p1_dmg = random.randint(min_dmg, max_dmg)

        p2_hp = p2_dat["health"]

        dodge_chance = random.randint(1, 10)
        atem = disnake.Embed(title="You Attack")

        if dodge_chance in [5, 9]:
            atem.description = f"**{p2}** Dodged the atack!"
            await self.inter.send(p1.mention, embed=atem)
            await asyncio.sleep(3)
            await self.menu(p2, p1)
            return
        else:
            # player attack
            enemy_hp_after = int(p2_hp) - int(p1_dmg)
            enemy_hp_after = max(enemy_hp_after, 0)
            atem.description = f"You Damaged **{p2}**\n**-{p1_dmg}HP**\ncurrent emeny hp: **{enemy_hp_after}HP**"

            atem.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
            )
            await self.inter.send(p1.mention, embed=atem)
            if enemy_hp_after <= 0:
                await asyncio.sleep(1)
                embed = disnake.Embed(title="You Won!", color=disnake.Colour.gold())
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/850983850665836544/878997428840329246/image0.png"
                )

                await self.inter.send(embed=embed)
                p1_dat["fighting"] = False
                p2_dat["fighting"] = False
                await self.inter.bot.players.update_one({"_id": p1.id}, {"$set": p1_dat})
                await self.inter.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
                print(f"{p1} and {p2} has ended the fight")
                return

            else:
                p2_dat["health"] = enemy_hp_after
                await self.inter.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
                await asyncio.sleep(2)
                await self.menu(p2, p1)

    async def weapon(self, inter, p1):
        data = await inter.bot.players.find_one({"_id": p1.id})
        data["inventory"].remove(item)
        data["inventory"].append(data["weapon"])
        data["weapon"] = item
        await inter.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await inter.send(f"Successfully equipped {item.title()}")
        await asyncio.sleep(2)
        return await self.menu(inter, p2, p1)  # replace

    async def armor(self, inter, p1, p2, item):
        data = await inter.bot.players.find_one({"_id": p1.id})
        print(str(item))
        data["inventory"].remove(item)
        data["inventory"].append(data["armor"])

        data["armor"] = item
        await inter.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await inter.send(f"Successfully equipped {item.title()}")
        await asyncio.sleep(2)
        return await self.attack(inter, p2, p1)

    async def food(self, inter, p1, p2, item):
        data = await inter.bot.players.find_one({"_id": p1.id})
        data["inventory"].remove(item)
        heal = inter.bot.items[item]["HP"]
        data["health"] += heal

        if data["health"] >= data["max_health"]:
            data["health"] = data["max_health"]
            await inter.bot.players.update_one({"_id": p1.id}, {"$set": data})
            await inter.send("Your health maxed out")
            await asyncio.sleep(2)
            return await self.menu(inter, p2, p1)  # replace
        health = data["health"]
        await inter.bot.players.update_one({"_id": p1.id}, {"$set": data})
        await inter.send(
            f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
        )
        await asyncio.sleep(2)
        return await self.menu(inter, p2, p1)  # replace

    async def use(self, inter, p1, p2):

        await create_player_info(inter, p1)
        data = await inter.bot.players.find_one({"_id": p1.id})
        if len(data["inventory"]) == 0:
            await inter.send("You have nothing to use")
            await asyncio.sleep(2)
            return await self.menu(inter, p1, p2)  # replace

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
            occurrence(store, data)
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

        msg = await inter.send(embed=embed, components=rows)

        on_click = msg.create_click_listener(timeout=120)

        @on_click.not_from_user(inter.author, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.from_user(inter.author)
        async def selected(inter):
            on_click.kill()
            selected_item = inter.component.id
            await msg.edit(components=[])
            try:
                await getattr(self, inter.bot.items[selected_item]["func"])(inter, p1, p2, selected_item)
            except KeyError:
                await inter.send("Nothing happened")
                await asyncio.sleep(2)
                return await self.menu(p2, p1)  # replace

    async def spare(self, inter, p1, p2):
        p1_dat = await inter.bot.players.find_one({"_id": p1.id})
        p2_dat = await inter.bot.players.find_one({"_id": p2.id})
        p1_dat["fighting"] = False
        p2_dat["fighting"] = False
        await inter.bot.players.update_one({"_id": p1.id}, {"$set": p1_dat})
        await inter.bot.players.update_one({"_id": p2.id}, {"$set": p2_dat})
        await inter.send(f"{p2.mention}\n\n{p1} has spared you!, battle is done")