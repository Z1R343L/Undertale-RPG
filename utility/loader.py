import time

async def create_player_info(ctx, mem):
    dat = await ctx.bot.players.find_one({"_id": mem.id})
    if dat is None:
        new_account = {
            "started": False,
            "registered_on" : int(time.time()),
            "multi_g": 1,
            "multi_xp": 1,
            "tokens": 0,
            "_id": mem.id,
            "name": mem.name,
            "health": 100,
            "damage": 0,
            "max_health": 100,
            "monster_hp": 0,
            "level": 1,
            "resets": 0,
            "kills": 0,
            "deaths": 0,
            "spares" : 0,
            "selected_monster": None,
            "last_monster": None,
            "exp": 0,
            "gold": 200,
            "armor": "bandage",
            "inventory": [],
            "weapon": "stick",
            "location": "ruins",
            "daily_block": 0,
            "supporter_block": 0,
            "booster_block" : 0,
            "rest_block": 0,
            "standard crate": 1,
            "determination crate": 0,
            "soul crate": 0,
            "void crate": 0
        }

        await ctx.bot.players.insert_one(new_account)
    else:
        return
