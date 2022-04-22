import asyncio
import random

import disnake
from disnake.ext import commands, components
from disnake.enums import ButtonStyle
import utility.loader as loader

from disnake.ui import Button, ActionRow

from utility import utils
import time

class battle:
    def __init__(
      self, 
      author: disnake.Member,
      bot: commands.AutoShardedBot, 
      monster: str,
      inter: disnake.CommandInteraction, 
      kind: int,
      channel: disnake.TextChannel
    ) -> None:
    
        self.bot = bot
        self.channel = channel
        self.author = author
        self.monster = monster
        self.inter = inter
        self.kind = kind  # 0 for monster, 1 for boss, 2 for special.
        
    async def count(keys, value):
        try:
            keys[str(value)] = keys[value] + 1
        except KeyError:
            keys[str(value)] = 1
            return

    # ending the fight with the id
    async def end(self):
      del self.bot.fights[str(self.author.id)]

    async def check_levelup(self):
        info = await self.bot.players.find_one({"_id": self.author.id})
        xp = info["exp"]
        num = 100
        lvl = info["level"]
        lvlexp = num * lvl
        if xp >= lvlexp:
            info["level"] = info["level"] + 1
            info["max_health"] = info["max_health"] + 4
            new_lvl = info["level"]
            new_dmg = info["damage"]

            data = {
                "level": info["level"],
                "exp": xp - lvlexp,
                "max_health": info["max_health"] + 4,
                "damage": info["damage"] + 1
            }
            await self.bot.players.update_one({"_id": author.id}, {"$set": data})
            embed = disnake.Embed(
                title="LOVE Increased",
                description=f"Your LOVE Increased to **{new_lvl}**\nDamage increased to {new_dmg}",
                color=disnake.Colour.red(),
            )
            await self.channel.send(inter.author.mention, embed=embed)
            for i in self.bot.locations:
                if self.bot.locations[i]["RQ_LV"] == info["level"]:
                    await self.channel.send(
                        f"Congrats, You unlocked {i}, you can go there by running /travel"
                    )
            return await self.check_levelup()
        else:
            return

    async def menu(self):

        info = await self.bot.players.find_one({"_id": self.author.id})

        buttons = [
            disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                label='Fight',
                custom_id=Fight.action.build_custom_id(action="attack", uid=self.author.id)
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.gray,
                label='Items',
                custom_id=Fight.action.build_custom_id(action="use", uid=self.author.id)
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label='Mercy',
                custom_id=Fight.action.build_custom_id(action="spare" ,uid=self.author.id)
            ),
        ]

        health = info["health"]
        monster = self.monster
        title = self.bot.monsters[monster]["title"]
        enemy_hp = info["monster_hp"]
        damage = self.bot.monsters[monster]["atk"]

        embed = disnake.Embed(
            title=f"{monster}, {title}",
            description=f"**Your HP is {health}\nMonster health: {enemy_hp}HP\ncan deal up to {damage}ATK**",
            color=disnake.Colour.blue()
        )
        image = self.bot.monsters[monster]["im"]
        embed.set_thumbnail(url=image)

        await self.inter.send(self.author.mention, embed=embed, components=buttons)

    async def attack(self):
        try:
            event = self.bot.events
            data = self.bot.monsters
            author = self.author
            info = await self.bot.players.find_one({"_id": self.author.id})
            user_wep = info["weapon"]
            monster = self.monster
            if monster is None:
                monster = info["last_monster"]
            damage = info["damage"]
            enemy_hp = info["monster_hp"]

            min_dmg = self.bot.items[user_wep]["min_dmg"]
            max_dmg = self.bot.items[user_wep]["max_dmg"]
            enemy_min_gold = data[monster]["min_gold"]
            enemy_max_gold = data[monster]["max_gold"]
            enemy_xp_min = data[monster]["min_xp"]
            enemy_xp_max = data[monster]["max_xp"]

            enemy_gold = random.randint(enemy_min_gold, enemy_max_gold)
            enemy_xp = random.randint(enemy_xp_min, enemy_xp_max)
            user_dmg = random.randint(min_dmg, max_dmg)

            dodge_chance = random.randint(1, 10)

            atem = disnake.Embed(title="You Attack")

            if dodge_chance in [5, 9]:
                atem.description = f"**{monster}** Dodged the attack!"
                await self.channel.send(self.author.mention, embed=atem)
                await asyncio.sleep(3)
                await self.counter_attack()
            else:
                # player attack
                damage = int(user_dmg) + int(damage)
                enemy_hp_after = int(enemy_hp) - damage
                enemy_hp_after = max(enemy_hp_after, 0)
                atem.description = f"You Damaged **{monster}**\n**-{user_dmg}HP**\ncurrent monster hp: **{enemy_hp_after}HP**"
                atem.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
                )
                await self.channel.send(self.author.mention, embed=atem)
                if enemy_hp_after <= 0:
                    await asyncio.sleep(1)
                    embed = disnake.Embed(
                        title="You Won!",
                        description=f"You Earned **{int(enemy_gold)} G** and **{int(enemy_xp)}XP**",
                        color=disnake.Colour.gold(),
                    )
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/850983850665836544/878997428840329246/image0.png"
                    )
                    xp_multi = int(info["multi_xp"])
                    gold_multi = int(info["multi_g"])
                    gold = enemy_gold
                    exp = enemy_xp
                    # Multiplier
                    if info["multi_g"] > 1 and info["multi_xp"] > 1:
                        gold = gold * info["multi_xp"]
                        exp = exp * info["multi_g"]
                        embed.description += f"\n\n**[MULTIPLIER]**\n> **[{xp_multi}x]** XP: **+{int(exp - enemy_xp)}** ({int(exp)})\n> **[{gold_multi}x]** GOLD: **+{int(gold - enemy_gold)}** ({int(gold)})"
                    # Events
                    if event is not None:
                        xp_multi = int(event["multi_xp"])
                        gold_multi = int(event["multi_g"])
                        gold = gold * event["multi_g"]
                        exp = exp * event["multi_xp"]
                        name = event["name"]

                        embed.description += f"\n\n**[{name.upper()} EVENT!]**\n> **[{xp_multi}x]** XP: **+{int(exp - enemy_xp)}** ({int(exp)})\n> **[{gold_multi}x]** GOLD: **+{int(gold - enemy_gold)}** ({int(gold)})"

                    info["selected_monster"] = None
                    info["monster_hp"] = 0
                    if self.kind == 1:
                        info["rest_block"] = time.time()

                    info["gold"] = info["gold"] + gold
                    info["exp"] = info["exp"] + exp

                    if len(self.bot.monsters[monster]["loot"]) > 0:
                        num = random.randint(0, 6)
                        crate = self.bot.monsters[monster]["loot"][0]
                        if num < 2:
                            info[crate] += 1
                            embed.description += (
                                f"\n\n**You got a {crate}, check u?crate command**"
                            )
                    info["kills"] = info["kills"] + 1
                    await self.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await self.check_levelup()
                    await self.channel.send(embed=embed)
                    print(f"{self.author} has ended the fight")
                    return await self.end()
                else:
                    info["monster_hp"] = enemy_hp_after
                    await self.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await asyncio.sleep(2)
                    return await self.counter_attack()

            return
        except Exception as e:
            await self.bot.get_channel(827651947678269510).send(e)
            await self.end()

    async def counter_attack(self):
        #try:
            author = self.author
            data = self.bot.monsters

            info = await self.bot.players.find_one({"_id": self.author.id})
            enemy_define = self.monster
            if enemy_define is None:
                enemy_define = info["last_monster"]
            enemy_dmg = data[enemy_define]["atk"]
            user_ar = info["armor"].lower()
            min_dfs = self.bot.items[user_ar]["min_dfs"]
            max_dfs = self.bot.items[user_ar]["max_dfs"]
            user_dfs = random.randint(min_dfs, max_dfs)
            user_hp = info["health"]
            user_max_hp = info["max_health"]

            enemy_dmg = enemy_dmg - int(user_dfs)
            if enemy_dmg <= 0:
                enemy_dmg = 1
                enemy_dmg = random.randint(enemy_dmg, enemy_dmg + 10)
            dodge_chance = random.randint(1, 10)
            atem = disnake.Embed(title=f"{enemy_define} Attacks")

            if dodge_chance >= 9:
                atem.description = f"**{self.author.name}** Dodged the attack!"
                await self.channel.send(self.author.mention, embed=atem)
                await asyncio.sleep(3)
                return await self.menu()

            user_hp_after = int(user_hp) - int(enemy_dmg)
            gold_lost = random.randint(10, 40) + info["level"]
            atem.description = f"**{enemy_define}** Attacks\n**-{enemy_dmg}HP**\ncurrent hp: **{user_hp_after}HP\n{await utils.get_bar(user_hp_after, user_max_hp)}**"
            atem.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
            )
            await asyncio.sleep(2)
            await self.channel.send(self.author.mention, embed=atem)

            if user_hp_after <= 0:
                info["gold"] = info["gold"] - gold_lost
                info["gold"] = max(info["gold"], 0)
                info["deaths"] = info["deaths"] + 1
                info["health"] = 10
                info["selected_monster"] = None
                info["monster_hp"] = 0
                await self.bot.players.update_one({"_id": self.author.id}, {"$set": info})

                await asyncio.sleep(3)
                femb = disnake.Embed(
                    title="You Lost <:broken_heart:865088299520753704>",
                    description=f"**Stay Determines please!, You lost {gold_lost} G**",
                    color=disnake.Colour.red(),
                )
                print(f"{self.author} has ended the fight (Died)")
                await self.channel.send(self.author.mention, embed=femb)
                return await self.end()
            else:
                info["health"] = user_hp_after
                await self.bot.players.update_one({"_id": self.author.id}, {"$set": info})
                await asyncio.sleep(3)
                return await self.menu()
              
        #except Exception as e:
            #await self.bot.get_channel(827651947678269510).send(e)
            #await self.end()

    async def weapon(self, item):
        try:
            data = await self.bot.players.find_one({"_id": self.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["weapon"])
            data["weapon"] = item
            await self.bot.players.update_one({"_id": self.author.id}, {"$set": data})
            await self.channel.send(f"Successfully equipped {item.title()}")

            return await self.counter_attack(self)
        except Exception as e:
            await self.bot.get_channel(827651947678269510).send(e)
            await self.end()

    async def armor(self, item):
        try:

            data = await self.bot.players.find_one({"_id": self.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["armor"])

            data["armor"] = item
            await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await self.send(f"Successfully equipped {item.title()}")

            return await self.counter_attack()

        except Exception as e:
            await self.bot.get_channel(827651947678269510).send(e)
            await self.end()

    async def food(self, item):
        try:
            data = await self.bot.players.find_one({"_id": self.author.id})
            data["inventory"].remove(item)
            heal = self.bot.items[item]["HP"]
            data["health"] += heal

            if data["health"] >= data["max_health"]:
                data["health"] = data["max_health"]
                await self.bot.players.update_one({"_id": self.author.id}, {"$set": data})
                await self.channel.send("Your health maxed out")
                return await self.counter_attack(self)
            health = data["health"]
            await inter.bot.players.update_one({"_id": self.author.id}, {"$set": data})
            await self.channel.send(
                f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
            )
            return await self.counter_attack()

        except Exception as e:
            await self.bot.get_channel(827651947678269510).send(e)
            await self.end()
    async def use(self):
        #try:
            await loader.create_player_info(self.inter, self.author)
            data = await self.bot.players.find_one({"_id": self.author.id})
            if len(data["inventory"]) == 0:
                await self.channel.send(f"{self.author.mention} You have nothing to use")
                return await battle.counter_attack()

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
            keys = {}
            for data in data["inventory"]:
                await self.count(keys, data)
            for k, v in keys.items():
                inventory.append({f"{k}": f"{v}x"})
            for item in inventory:
                for key in item:
                    lista.append(
                        Button(
                            label=f"{key.title()} {item[key]}",
                            custom_id=Fight.food.build_custom_id(item=key.lower(), author=self.author),
                            style=ButtonStyle.grey
                        )
                    )

            for i in range(0, len(lista), 5):
                rows.append(ActionRow(*lista[i: i + 5]))

            await self.channel.send(embed=embed, components=rows)

    async def spare(self):
        try:
            info = await self.bot.players.find_one({"_id": self.author.id})
            monster = info["selected_monster"]
            if monster is None:
                monster = info["last_monster"]

            if monster == "sans":
                await inter.send(
                    "Get dunked on!!, if were really friends... **YOU WON'T COME BACK**"
                )
                info["selected_monster"] = None
                self.bot.fights.remove(self.author.id)
                info["health"] = 10
                # if str(inter.invoked_with) == "fboss":
                #     info["rest_block"] = time.time()
                #     await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": info})
                #     return

            func = ["spared", "NotSpared", "spared"]
            monster = info["selected_monster"]
            sprfunc = random.choice(func)
            embed1 = disnake.Embed(
                title="Mercy", description=f"You tried to spare {monster}"
            )
            embed1.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803887253927100436/image0.png"
            )
            msg = await self.channel.send(self.author.mention, embed=embed1)
            await asyncio.sleep(5)
            embed2 = disnake.Embed(
                title="Mercy", description="They didn't accepted your mercy"
            )

            embed2.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803889297936613416/image0.png"
            )
            embed3 = disnake.Embed(title="Mercy", description="They accepted your mercy")
            embed3.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803887253927100436/image0.png"
            )
            if sprfunc == "spared":
                if self.kind == 1:
                    info["rest_block"] = time.time()

                info["selected_monster"] = None
                print(f"{self.author} has ended the fight (sparing)")
                # inter.command.reset_cooldown(inter)
                await msg.edit(embed=embed3)
                await self.bot.players.update_one({"_id": self.author.id}, {"$set": info})
                await self.end()
            elif sprfunc == "NotSpared":
                await msg.edit(embed=embed2)

                await asyncio.sleep(4)
                await self.counter_attack()

        except Exception as e:
            await self.bot.get_channel(827651947678269510).send(e)
            await self.end()


class Fight(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    class Choose(disnake.ui.View):
        def __init__(self, member: disnake.Member = None):
            super().__init__()
            self.choice = None
            self.author = member


        @disnake.ui.button(label="Boss", style=disnake.ButtonStyle.green, disabled=None)
        async def boss(self, button: disnake.Button, inter: disnake.MessageInteraction):
            if self.author == inter.author:
                self.choice = "boss"
                self.stop()
                return

        @disnake.ui.button(label="Monster", style=disnake.ButtonStyle.green)
        async def monster(self,button: disnake.Button, inter:disnake.MessageInteraction):
            if self.author == inter.author:
                self.choice = "monster"
                self.stop()
                return
            
    @components.component_listener()
    async def food(self, inter: disnake.MessageInteraction, item: str, author: disnake.Member) -> None:
        if inter.author != author:
            await inter.send('This is not yours kiddo!', ephemeral=True)
            return

        await inter.response.defer()

        msg = await inter.original_message()
        row = await utils.disable_all(msg)

        await inter.edit_original_message(components=row)

        return await getattr(battle, inter.bot.items[item]["func"])(self, inter, item)
            
    @components.component_listener()
    async def action(self, inter: disnake.MessageInteraction, action: str, uid: int) -> None:
        if inter.author.id != uid:
            await inter.send('This is not yours kiddo!', ephemeral=True)
            return

        await inter.response.defer()
        msg = await inter.original_message()
        row = await utils.disable_all(msg)

        await inter.edit_original_message(components=row)
        
        return await getattr(inter.bot.fights[str(uid)], action)()


    @commands.slash_command()
    async def boss(self, inter):

        if str(inter.author.id) in inter.bot.fights:
            return

        await loader.create_player_info(inter, inter.author)
        data = await inter.bot.players.find_one({"_id": inter.author.id})

        curr_time = time.time()
        delta = int(curr_time) - int(data["rest_block"])

        if 1800.0 >= delta > 0:
            seconds = 1800 - delta
            em = disnake.Embed(
                description=f"**You can't fight a boss yet!**\n\n**You can fight a boss <t:{int(time.time()) + int(seconds)}:R>**",
                color=disnake.Color.red(),
            )
            em.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/850983850665836544/878024511302271056/image0.png"
            )
            await inter.send(embed=em)
            return

        location = data["location"]
        random_monster = []

        for i in inter.bot.monsters:
            if inter.bot.monsters[i]["location"] == location:
                if inter.bot.monsters[i]["boss"]:
                    random_monster.append(i)
                else:
                    continue

        monster = random.choice(random_monster)

        info = inter.bot.monsters

        mon_hp_min = info[monster]["min_hp"]
        mon_hp_max = info[monster]["max_hp"]

        enemy_hp = random.randint(mon_hp_min, mon_hp_max)

        output = {
            "selected_monster": monster,
            "monster_hp": enemy_hp,
            "last_monster": monster
        }

        await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": output})
        print(f"{inter.author} has entered a fight")
        inter.bot.fights.append(inter.author.id)
        fight = battle(inter.author, inter.bot, monster, inter, 1, inter.channel)
        return await fight.menu()

    @commands.slash_command()
    async def fight(self, inter):
        """Fight Monsters and gain EXP and Gold"""
        if inter.author.id in inter.bot.fights:
            return

        await loader.create_player_info(inter, inter.author)
        data = await inter.bot.players.find_one({"_id": inter.author.id})


        location = data["location"]
        random_monster = []

        for i in inter.bot.monsters:
            if inter.bot.monsters[i]["location"] == location:
                if inter.bot.monsters[i]["boss"]:
                    continue
                else:
                    random_monster.append(i)

        info = inter.bot.monsters

        if len(random_monster) == 0:
            await inter.send(f"There are no monsters here?, You are for sure inside a /boss area only!")
            return

        monster = random.choice(random_monster)

        mon_hp_min = info[monster]["min_hp"]
        mon_hp_max = info[monster]["max_hp"]

        enemy_hp = random.randint(mon_hp_min, mon_hp_max)

        output = {
            "selected_monster": monster,
            "monster_hp": enemy_hp,
            "last_monster": monster
        }

        await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": output})
        print(f"{inter.author} has entered a fight")
        fight = battle(inter.author, inter.bot, monster, inter, 0, inter.channel)
        fight.bot.fights[str(inter.author.id)] = fight
        return await fight.menu()

def setup(bot):
    bot.add_cog(Fight(bot))