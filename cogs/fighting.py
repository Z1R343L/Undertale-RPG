import asyncio
import random
import time

import discord
from discord.ext import commands
from dislash import *

import botTools.loader as loader


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


class battle:

    async def check_levelup(self, ctx):
        author = ctx.author
        info = await ctx.bot.players.find_one({"_id": author.id})
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
            await ctx.bot.players.update_one({"_id": author.id}, {"$set": data})
            embed = discord.Embed(
                title="LOVE Increased",
                description=f"Your LOVE Increased to **{new_lvl}**\nDamage increased to {new_dmg}",
                color=discord.Colour.red(),
            )
            await ctx.send(ctx.author.mention, embed=embed)
            for i in ctx.bot.locations:
                if ctx.bot.locations[i]["RQ_LV"] == info["level"]:
                    await ctx.send(
                        f"Congrats, You unlocked {i}, you can go there by running {ctx.prefix}travel"
                    )
            return await battle.check_levelup(self, ctx)
        else:
            return

    async def menu(self, ctx):
        row = ActionRow(
            Button(style=ButtonStyle.red, label="Fight", custom_id="fight"),
            # Button(style=ButtonStyle.gray, label="Act", custom_id="act"),
            Button(style=ButtonStyle.gray, label="Items", custom_id="items"),
            Button(style=ButtonStyle.green, label="mercy", custom_id="spare"),
        )

        player = ctx.author

        info = await ctx.bot.players.find_one({"_id": player.id})

        health = info["health"]
        monster = info["selected_monster"]
        title = ctx.bot.monsters[monster]["title"]
        enemy_hp = info["monster_hp"]
        damage = ctx.bot.monsters[monster]["atk"]

        embed = discord.Embed(
            title=f"{monster}, {title}",
            description=f"**Your HP is {health}\nMonster health: {enemy_hp}HP\ncan deal up to {damage}ATK**",
            color=discord.Colour.blue()
        )

        image = ctx.bot.monsters[monster]["im"]
        embed.set_thumbnail(url=image)

        msg = await ctx.send(player.mention, embed=embed, components=[row])
        on_click = msg.create_click_listener(timeout=40)
        row.disable_buttons()

        @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
        async def on_wrong_user(inter):
            # Reply with a hidden message
            await inter.reply("This is not yours kiddo!", ephemeral=True)

        @on_click.matching_id("fight")
        async def on_test_button(inter, reset_timeout=False):
            on_click.kill()
            await msg.edit(components=[row])
            return await battle.attack(self, ctx, inter)

        # @on_click.matching_id("act")
        # async def on_test_button(inter, reset_timeout=False):
        # await msg.edit(components=[])
        # on_click.kill()
        # return await Act.act(self, ctx)

        @on_click.matching_id("items")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[row])
            on_click.kill()
            return await battle.use(self, ctx, inter)

        @on_click.matching_id("spare")
        async def on_test_button(inter, reset_timeout=False):
            await msg.edit(components=[row])
            on_click.kill()
            return await battle.spare(self, ctx, inter)

        @on_click.timeout
        async def on_timeout():
            row.disable_buttons()
            embed.description = "You took too much to reply!"
            try:
                await msg.edit(embed=embed, components=[row])
            except:
                pass
            data = {
                "selected_monster": None
            }
            print(f"{ctx.author} has ended the fight (timing out)")
            ctx.command.reset_cooldown(ctx)
            ctx.bot.fights.remove(ctx.author.id)
            return await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})

    async def attack(self, ctx, inter):
        try:
            event = ctx.bot.events
            data = ctx.bot.monsters
            author = ctx.author
            info = await ctx.bot.players.find_one({"_id": author.id})
            user_wep = info["weapon"]
            monster = info["selected_monster"]
            if monster is None:
                monster = info["last_monster"]
            damage = info["damage"]
            enemy_hp = info["monster_hp"]

            min_dmg = ctx.bot.items[user_wep]["min_dmg"]
            max_dmg = ctx.bot.items[user_wep]["max_dmg"]
            enemy_min_gold = data[monster]["min_gold"]
            enemy_max_gold = data[monster]["max_gold"]
            enemy_xp_min = data[monster]["min_xp"]
            enemy_xp_max = data[monster]["max_xp"]

            enemy_gold = random.randint(enemy_min_gold, enemy_max_gold)
            enemy_xp = random.randint(enemy_xp_min, enemy_xp_max)
            user_dmg = random.randint(min_dmg, max_dmg)

            dodge_chance = random.randint(1, 10)

            atem = discord.Embed(title="You Attack")

            if dodge_chance in [5, 9]:
                atem.description = f"**{monster}** Dodged the attack!"
                await inter.send(ctx.author.mention, embed=atem)
                await asyncio.sleep(3)
                await battle.counter_attack(self, ctx)
            else:
                # player attack
                damage = int(user_dmg) + int(damage)
                enemy_hp_after = int(enemy_hp) - damage
                enemy_hp_after = max(enemy_hp_after, 0)
                atem.description = f"You Damaged **{monster}**\n**-{user_dmg}HP**\ncurrent monster hp: **{enemy_hp_after}HP**"
                atem.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
                )
                await inter.send(ctx.author.mention, embed=atem)
                if enemy_hp_after <= 0:
                    await asyncio.sleep(1)
                    embed = discord.Embed(
                        title="You Won!",
                        description=f"You Earned **{int(enemy_gold)} G** and **{int(enemy_xp)}XP**",
                        color=discord.Colour.gold(),
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
                    ctx.bot.fights.remove(ctx.author.id)
                    if ctx.invoked_with in ctx.bot.cmd_list:
                        info["rest_block"] = time.time()

                    info["gold"] = info["gold"] + gold
                    info["exp"] = info["exp"] + exp

                    if len(ctx.bot.monsters[monster]["loot"]) > 0:
                        num = random.randint(0, 6)
                        crate = ctx.bot.monsters[monster]["loot"][0]
                        if num < 2:
                            info[crate] += 1
                            embed.description += (
                                f"\n\n**You got a {crate}, check u?crate command**"
                            )
                    info["kills"] = info["kills"] + 1
                    await ctx.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await battle.check_levelup(self, ctx)
                    await ctx.send(embed=embed)
                    print(f"{ctx.author} has ended the fight")
                    ctx.command.reset_cooldown(ctx)
                else:
                    info["monster_hp"] = enemy_hp_after
                    await ctx.bot.players.update_one({"_id": author.id}, {"$set": info})
                    await asyncio.sleep(2)
                    return await battle.counter_attack(self, ctx)

            return
        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def counter_attack(self, ctx):
        try:
            author = ctx.author
            data = ctx.bot.monsters

            info = await ctx.bot.players.find_one({"_id": ctx.author.id})
            enemy_define = info["selected_monster"]
            if enemy_define is None:
                enemy_define = info["last_monster"]
            enemy_dmg = data[enemy_define]["atk"]
            user_ar = info["armor"].lower()
            min_dfs = ctx.bot.items[user_ar]["min_dfs"]
            max_dfs = ctx.bot.items[user_ar]["max_dfs"]
            user_dfs = random.randint(min_dfs, max_dfs)
            user_hp = info["health"]
            user_max_hp = info["max_health"]

            enemy_dmg = enemy_dmg - int(user_dfs)
            if enemy_dmg <= 0:
                enemy_dmg = 1
                enemy_dmg = random.randint(enemy_dmg, enemy_dmg + 10)
            dodge_chance = random.randint(1, 10)
            atem = discord.Embed(title=f"{enemy_define} Attacks")

            if dodge_chance >= 9:
                atem.description = f"**{ctx.author.name}** Dodged the attack!"
                await ctx.send(ctx.author.mention, embed=atem)
                await asyncio.sleep(3)
                return await battle.menu(self, ctx)

            user_hp_after = int(user_hp) - int(enemy_dmg)
            gold_lost = random.randint(10, 40) + info["level"]
            atem.description = f"**{enemy_define}** Attacks\n**-{enemy_dmg}HP**\ncurrent hp: **{user_hp_after}HP\n{await get_bar(user_hp_after, user_max_hp)}**"
            atem.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803885802588733460/image0.png"
            )
            await asyncio.sleep(2)
            await ctx.send(ctx.author.mention, embed=atem)

            if user_hp_after <= 0:
                info["gold"] = info["gold"] - gold_lost
                info["gold"] = max(info["gold"], 0)
                info["deaths"] = info["deaths"] + 1
                info["health"] = 10
                ctx.bot.fights.remove(ctx.author.id)
                info["selected_monster"] = None
                info["monster_hp"] = 0
                await ctx.bot.players.update_one({"_id": author.id}, {"$set": info})

                await asyncio.sleep(3)
                femb = discord.Embed(
                    title="You Lost <:broken_heart:865088299520753704>",
                    description=f"**Stay Determines please!, You lost {gold_lost} G**",
                    color=discord.Colour.red(),
                )
                print(f"{ctx.author} has ended the fight (Died)")
                ctx.command.reset_cooldown(ctx)
                await ctx.send(ctx.author.mention, embed=femb)
                return
            else:
                info["health"] = user_hp_after
                await ctx.bot.players.update_one({"_id": author.id}, {"$set": info})
                await asyncio.sleep(3)
                return await battle.menu(self, ctx)
        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def weapon(self, ctx, item):
        try:
            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["weapon"])
            data["weapon"] = item
            await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
            await ctx.send(f"Successfully equipped {item.title()}")

            return await battle.counter_attack(self, ctx)
        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def armor(self, ctx, item):
        try:

            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            data["inventory"].remove(item)
            data["inventory"].append(data["armor"])

            data["armor"] = item
            await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
            await ctx.send(f"Successfully equipped {item.title()}")

            return await battle.counter_attack(self, ctx)

        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def food(self, ctx, item):
        try:
            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            data["inventory"].remove(item)
            heal = ctx.bot.items[item]["HP"]
            data["health"] += heal

            if data["health"] >= data["max_health"]:
                data["health"] = data["max_health"]
                await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
                await ctx.send("Your health maxed out")
                return await battle.counter_attack(self, ctx)
            health = data["health"]
            await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": data})
            await ctx.send(
                f"You consumed {item}, restored {heal}HP\n\nCurrent health: {health}HP"
            )
            return await battle.counter_attack(self, ctx)

        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def use(self, ctx, inter):
        try:
            await loader.create_player_info(ctx, ctx.author)
            data = await ctx.bot.players.find_one({"_id": ctx.author.id})
            if len(data["inventory"]) == 0:
                await ctx.send("You have nothing to use")
                return await battle.counter_attack(self, ctx)

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
            keys = {}
            for data in data["inventory"]:
                await count(keys, data)
            for k, v in keys.items():
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

            msg = await inter.reply(embed=embed, components=rows)

            on_click = msg.create_click_listener(timeout=120)

            @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
            async def on_wrong_user(intr):
                await intr.reply("This is not yours kiddo!", ephemeral=True)

            @on_click.from_user(ctx.author)
            async def selected(intr):
                on_click.kill()
                selected_item = intr.component.id
                await msg.edit(components=[])
                try:
                    await getattr(battle, ctx.bot.items[selected_item]["func"])(self, ctx, selected_item)
                except KeyError:
                    await ctx.send("Nothing happened")
                    await asyncio.sleep(2)
                    return await battle.counter_attack(self, ctx)
        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)

    async def spare(self, ctx, inter):
        try:
            info = await ctx.bot.players.find_one({"_id": ctx.author.id})
            monster = info["selected_monster"]
            if monster is None:
                monster = info["last_monster"]

            if monster == "sans":
                await ctx.send(
                    "Get dunked on!!, if were really friends... **YOU WON'T COME BACK**"
                )
                info["selected_monster"] = None
                ctx.bot.fights.remove(ctx.author.id)
                info["health"] = 10
                if str(ctx.invoked_with) == "fboss":
                    info["rest_block"] = time.time()
                    await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": info})
                    return

            func = ["spared", "NotSpared", "spared"]
            monster = info["selected_monster"]
            sprfunc = random.choice(func)
            embed1 = discord.Embed(
                title="Mercy", description=f"You tried to spare {monster}"
            )
            embed1.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803887253927100436/image0.png"
            )
            msg = await inter.reply(embed=embed1)
            await asyncio.sleep(5)
            embed2 = discord.Embed(
                title="Mercy", description="They didn't accepted your mercy"
            )

            embed2.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803889297936613416/image0.png"
            )
            embed3 = discord.Embed(title="Mercy", description="They accepted your mercy")
            embed3.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/793382520665669662/803887253927100436/image0.png"
            )
            if sprfunc == "spared":
                if str(ctx.invoked_with) in ctx.bot.cmd_list:
                    info["rest_block"] = time.time()
                info["selected_monster"] = None
                ctx.bot.fights.remove(ctx.author.id)
                print(f"{ctx.author} has ended the fight (sparing)")
                ctx.command.reset_cooldown(ctx)
                await msg.edit(embed=embed3)
                await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": info})
            elif sprfunc == "NotSpared":
                await msg.edit(embed=embed2)

                await asyncio.sleep(4)
                await battle.counter_attack(self, ctx)

        except Exception as e:
            ctx.bot.fights.remove(ctx.author.id)
            await ctx.bot.get_channel(827651947678269510).send(e)


class Fight(commands.Cog):

    def __init_(self, bot):
        self.bot = bot

    @commands.command(aliases=["f", "boss", "fboss", "bossfight"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fight(self, ctx):
        """Fight Monsters and gain EXP and Gold"""
        if ctx.author.id in ctx.bot.fights:
            return

        await loader.create_player_info(ctx, ctx.author)
        data = await ctx.bot.players.find_one({"_id": ctx.author.id})
        if ctx.invoked_with in ctx.bot.cmd_list:
            curr_time = time.time()
            delta = int(curr_time) - int(data["rest_block"])

            if 1800.0 >= delta > 0:
                seconds = 1800 - delta
                em = discord.Embed(
                    description=f"**You can't fight a boss yet!**\n\n**You can fight a boss <t:{int(time.time()) + int(seconds)}:R>**",
                    color=discord.Color.red(),
                )
                em.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/850983850665836544/878024511302271056/image0.png"
                )
                await ctx.send(embed=em)
                ctx.command.reset_cooldown(ctx)
                return

        location = data["location"]
        random_monster = []

        for i in ctx.bot.monsters:
            if ctx.bot.monsters[i]["location"] == location:
                if ctx.bot.monsters[i]["boss"] and ctx.invoked_with in ctx.bot.cmd_list:
                    random_monster.append(i)
                elif (
                        ctx.bot.monsters[i]["boss"] is False
                        and ctx.invoked_with not in ctx.bot.cmd_list
                ):
                    random_monster.append(i)
                else:
                    pass

        info = ctx.bot.monsters

        if len(random_monster) == 0:
            await ctx.send(f"There are no monsters here?, Are you in an only boss area?, {ctx.prefix}boss")
            ctx.command.reset_cooldown(ctx)
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

        await ctx.bot.players.update_one({"_id": ctx.author.id}, {"$set": output})
        print(f"{ctx.author} has entered a fight")
        ctx.bot.fights.append(ctx.author.id)
        return await battle.menu(self, ctx)


def setup(bot):
    bot.add_cog(Fight(bot))
