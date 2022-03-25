import asyncio
import random
import time

import disnake
from disnake.ext import commands, components
from disnake.enums import ButtonStyle
import utility.loader as loader

from disnake.ui import Button, ActionRow

import utility.utils


class battle:

    async def count(keys, value):
        try:
            keys[str(value)] = keys[value] + 1
        except KeyError:
            keys[str(value)] = 1
            return


    async def get_bar(health, max_health):
        bar0 = "<:0_:899376245496758343>"
        bar2 = "<:2_:899376429568000040>"
        bar3 = "<:3_:899376559700451379>"
        bar4 = "<:4_:899376608220172339>"
        bar5 = "<:5_:899376657759088750>"
        bar = None
        mix = health / max_health
        per = mix * 100
        if per == 0:
            bar = f"{bar0}{bar0}{bar0}{bar0}{bar0}"
        if 10 >= per > 0:
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
            bar = f"{bar5}{bar5}{bar5}{bar3}{bar0}"
        if 80 >= per > 70:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar2}"
        if 90 >= per > 80:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar4}"
        if 100 >= per > 90:
            bar = f"{bar5}{bar5}{bar5}{bar5}{bar5}"
        return bar

    async def check_levelup(self, inter):
        author = inter.author
        info = await inter.bot.players.find_one({"_id": author.id})
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
            await inter.bot.players.update_one({"_id": author.id}, {"$set": data})
            embed = disnake.Embed(
                title="LOVE Increased",
                description=f"Your LOVE Increased to **{new_lvl}**\nDamage increased to {new_dmg}",
                color=disnake.Colour.red(),
            )
            await inter.send(inter.author.mention, embed=embed)
            for i in inter.bot.locations:
                if inter.bot.locations[i]["RQ_LV"] == info["level"]:
                    await inter.send(
                        f"Congrats, You unlocked {i}, you can go there by running {inter.prefix}travel"
                    )
            return await battle.check_levelup(self, inter)
        else:
            return

    async def menu(self, inter, uid):

        player = inter.author

        info = await inter.bot.players.find_one({"_id": player.id})

        buttons = [
            disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                label='Fight',
                custom_id=f"fight:{uid}"
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.gray,
                label='Items',
                custom_id=f"items:{uid}"
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label='Mercy',
                custom_id=f"spare:{uid}"
            ),
        ]

        health = info["health"]
        monster = info["selected_monster"]
        title = inter.bot.monsters[monster]["title"]
        enemy_hp = info["monster_hp"]
        damage = inter.bot.monsters[monster]["atk"]

        embed = disnake.Embed(
            title=f"{monster}, {title}",
            description=f"**Your HP is {health}\nMonster health: {enemy_hp}HP\ncan deal up to {damage}ATK**",
            color=disnake.Colour.blue()
        )
        image = inter.bot.monsters[monster]["im"]
        embed.set_thumbnail(url=image)

        msg = await inter.send(player.mention, embed=embed, components=buttons)

    async def attack(self, inter):
        try:
            event = inter.bot.events
            data = inter.bot.monsters
            author = inter.author
            info = await inter.bot.players.find_one({"_id": author.id})
            user_wep = info["weapon"]
            monster = info["selected_monster"]
            if monster is None:
                monster = info["last_monster"]
            damage = info["damage"]
            enemy_hp = info["monster_hp"]

            min_dmg = inter.bot.items[user_wep]["min_dmg"]
            max_dmg = inter.bot.items[user_wep]["max_dmg"]
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
                await inter.send(inter.author.mention, embed=atem)
                await asyncio.sleep(3)
                await battle.counter_attack(self, inter)
            else:
                # player attack
                damage = int(user_dmg) + int(damage)
                enemy_hp_after = int(enemy_hp) - damage
                enemy_hp_after = max(enemy_hp_after, 0)
                atem.description = f"You Damaged **{monster}**\n**-{user_dmg}HP**\ncurrent monster hp: **{enemy_hp_after}HP**"
                atem.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
                )
                await inter.send(inter.author.mention, embed=atem)
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
                    inter.bot.fights.remove(inter.author.id)
                    # if inter.invoked_with in inter.bot.cmd_list:
                    #     info["rest_block"] = time.time()

                    info["gold"] = info["gold"] + gold
                    info["exp"] = info["exp"] + exp

                    if len(inter.bot.monsters[monster]["loot"]) > 0:
                        num = random.randint(0, 6)
                        crate = inter.bot.monsters[monster]["loot"][0]
                        if num < 2:
                            info[crate] += 1
                            embed.description += (
                                f"\n\n**You got a {crate}, check u?crate command**"
                            )
                    info["kills"] = info["kills"] + 1
                    await inter.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await battle.check_levelup(self, inter)
                    await inter.send(embed=embed)
                    print(f"{inter.author} has ended the fight")
                else:
                    info["monster_hp"] = enemy_hp_after
                    await inter.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await asyncio.sleep(2)
                    return await battle.counter_attack(self, inter)

            return
        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)

    async def counter_attack(self, inter):
        try:
            author = inter.author
            data = inter.bot.monsters

            info = await inter.bot.players.find_one({"_id": inter.author.id})
            enemy_define = info["selected_monster"]
            if enemy_define is None:
                enemy_define = info["last_monster"]
            enemy_dmg = data[enemy_define]["atk"]
            user_ar = info["armor"].lower()
            min_dfs = inter.bot.items[user_ar]["min_dfs"]
            max_dfs = inter.bot.items[user_ar]["max_dfs"]
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
                atem.description = f"**{inter.author.name}** Dodged the attack!"
                await inter.send(inter.author.mention, embed=atem)
                await asyncio.sleep(3)
                return await battle.menu(self, inter, uid=inter.author.id)

            user_hp_after = int(user_hp) - int(enemy_dmg)
            gold_lost = random.randint(10, 40) + info["level"]
            atem.description = f"**{enemy_define}** Attacks\n**-{enemy_dmg}HP**\ncurrent hp: **{user_hp_after}HP\n{await battle.get_bar(user_hp_after, user_max_hp)}**"
            atem.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
            )
            await asyncio.sleep(2)
            await inter.send(inter.author.mention, embed=atem)

            if user_hp_after <= 0:
                info["gold"] = info["gold"] - gold_lost
                info["gold"] = max(info["gold"], 0)
                info["deaths"] = info["deaths"] + 1
                info["health"] = 10
                inter.bot.fights.remove(inter.author.id)
                info["selected_monster"] = None
                info["monster_hp"] = 0
                await inter.bot.players.update_one({"_id": author.id}, {"$set": info})

                await asyncio.sleep(3)
                femb = disnake.Embed(
                    title="You Lost <:broken_heart:865088299520753704>",
                    description=f"**Stay Determines please!, You lost {gold_lost} G**",
                    color=disnake.Colour.red(),
                )
                print(f"{inter.author} has ended the fight (Died)")
                # inter.command.reset_cooldown(inter)
                await inter.send(inter.author.mention, embed=femb)
                return
            else:
                info["health"] = user_hp_after
                await inter.bot.players.update_one({"_id": author.id}, {"$set": info})
                await asyncio.sleep(3)
                return await battle.menu(self, inter, uid=inter.author.id)
        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)

    async def weapon(self, inter, item):
        try:
            data = await inter.bot.players.find_one({"_id": inter.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["weapon"])
            data["weapon"] = item
            await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await inter.send(f"Successfully equipped {item.title()}")

            return await battle.counter_attack(self, inter)
        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)

    async def armor(self, inter, item):
        try:

            data = await inter.bot.players.find_one({"_id": inter.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["armor"])

            data["armor"] = item
            await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await inter.send(f"Successfully equipped {item.title()}")

            return await battle.counter_attack(self, inter)

        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)

    async def food(self, inter, item):
        try:
            data = await inter.bot.players.find_one({"_id": inter.author.id})
            data["inventory"].remove(item)
            heal = inter.bot.items[item]["HP"]
            data["health"] += heal

            if data["health"] >= data["max_health"]:
                data["health"] = data["max_health"]
                await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
                await inter.send("Your health maxed out")
                return await battle.counter_attack(self, inter)
            health = data["health"]
            await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await inter.send(
                f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
            )
            return await battle.counter_attack(self, inter)

        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)

    async def use(self, inter):
        #try:
            await loader.create_player_info(inter, inter.author)
            data = await inter.bot.players.find_one({"_id": inter.author.id})
            if len(data["inventory"]) == 0:
                await inter.send("You have nothing to use")
                return await battle.counter_attack(self, inter)

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
                await battle.count(keys, data)
            for k, v in keys.items():
                inventory.append({f"{k}": f"{v}x"})
            for item in inventory:
                for key in item:
                    lista.append(
                        Button(
                            label=f"{key.title()} {item[key]}",
                            custom_id=f"food:{key.lower()}:{inter.author.id}",
                            style=ButtonStyle.grey
                        )
                    )

            for i in range(0, len(lista), 5):
                rows.append(ActionRow(*lista[i: i + 5]))

            await inter.send(embed=embed, components=rows)

    async def spare(self, inter):
        try:
            info = await inter.bot.players.find_one({"_id": inter.author.id})
            monster = info["selected_monster"]
            if monster is None:
                monster = info["last_monster"]

            if monster == "sans":
                await inter.send(
                    "Get dunked on!!, if were really friends... **YOU WON'T COME BACK**"
                )
                info["selected_monster"] = None
                inter.bot.fights.remove(inter.author.id)
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
            msg = await inter.channel.send(embed=embed1)
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
                #if str(inter.invoked_with) in inter.bot.cmd_list:
                    #info["rest_block"] = time.time()
                info["selected_monster"] = None
                inter.bot.fights.remove(inter.author.id)
                print(f"{inter.author} has ended the fight (sparing)")
                # inter.command.reset_cooldown(inter)
                await msg.edit(embed=embed3)
                await inter.bot.players.update_one({"_id": inter.author.id}, {"$set": info})
            elif sprfunc == "NotSpared":
                await msg.edit(embed=embed2)

                await asyncio.sleep(4)
                await battle.counter_attack(self, inter)

        except Exception as e:
            inter.bot.fights.remove(inter.author.id)
            await inter.bot.get_channel(827651947678269510).send(e)


class Fight(commands.Cog):

    def __init_(self, bot):
        self.bot = bot

    @commands.command(aliases=["f", "boss", "fboss", "bossfight"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fight(self, inter):
        """Fight Monsters and gain EXP and Gold"""
        if inter.author.id in inter.bot.fights:
            return

        await loader.create_player_info(inter, inter.author)
        data = await inter.bot.players.find_one({"_id": inter.author.id})
        """
        if inter.invoked_with in inter.bot.cmd_list:
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
                inter.command.reset_cooldown(inter)
                return
        """
        location = data["location"]
        random_monster = []

        for i in inter.bot.monsters:
            if inter.bot.monsters[i]["location"] == location:
                #if inter.bot.monsters[i]["boss"] and inter.invoked_with in inter.bot.cmd_list:
                #    random_monster.append(i)
                #elif (
                #        inter.bot.monsters[i]["boss"] is False
                #        and inter.invoked_with not in inter.bot.cmd_list
                #):
                    random_monster.append(i)
                #else:
                #    pass

        info = inter.bot.monsters

        if len(random_monster) == 0:
            await inter.send(f"There are no monsters here?, Are you in an only boss area?, {inter.prefix}boss")
            #inter.command.reset_cooldown(inter)
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
        inter.bot.fights.append(inter.author.id)
        return await battle.menu(self, inter, uid=inter.author.id)

    @components.button_with_id(regex=r'fight:(?P<uid>\d+)')
    async def f_b(self, inter: disnake.MessageInteraction, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()
        msg = await inter.original_message()
        row = await utility.utils.disable_all(msg)

        await inter.edit_original_message(components=row)
        return await battle.attack(self, inter)

    @components.button_with_id(regex=r'items:(?P<uid>\d+)')
    async def i_b(self, inter: disnake.MessageInteraction, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()

        msg = await inter.original_message()
        row = await utility.utils.disable_all(msg)

        await inter.edit_original_message(components=row)
        return await battle.use(self, inter)

    @components.button_with_id(regex=r'spare:(?P<uid>\d+)')
    async def m_b(self, inter: disnake.MessageInteraction, uid: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()
        msg = await inter.original_message()
        row = await utility.utils.disable_all(msg)

        await inter.edit_original_message(components=row)
        return await battle.spare(self, inter)

    @components.button_with_id(regex=r'food:(?P<item>\D+):(?P<uid>\d+)')
    async def fr_b(self, inter: disnake.MessageInteraction, uid: str, item: str) -> None:
        if inter.author.id != int(uid):
            await inter.send('This is not your kiddo!', ephemeral=True)
            return

        await inter.response.defer()

        msg = await inter.original_message()
        row = await utility.utils.disable_all(msg)

        await inter.edit_original_message(components=row)

        return await getattr(battle, inter.bot.items[item]["func"])(self, inter, item)

def setup(bot):
    bot.add_cog(Fight(bot))
