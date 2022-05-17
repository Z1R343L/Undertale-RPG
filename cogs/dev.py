import disnake
from disnake.ext import commands

from utility.utils import get_all_funcs

class Developer_Tools(commands.Cog):
    """A Module for the developer tools"""


    def __init__(self, bot):
        self.bot = bot
        self.cmds = get_all_funcs(self)

    @commands.slash_command()
    @commands.is_owner()
    async def spit(self, inter, member: disnake.User = None):
        member = member or inter.author
        info = await inter.bot.players.find_one({"_id": member.id})
        await inter.send(info)

    @commands.slash_command()
    @commands.is_owner()
    async def fix(self, inter):
        """Fix, duh?"""
        for i in self.bot.fights:
            try:
                await self.bot.fights[i].end()
            except:
                del self.bot.fights[i]
        await inter.send("Done!")

    @commands.slash_command()
    @commands.is_owner()
    async def fix_shop(self, inter):
        for i in self.bot.shops:
            try:
                await self.bot.shops[i].end()
            except:
                del self.bot.shops[i]

        await inter.send("Done!")

    @commands.slash_command()
    @commands.is_owner()
    async def in_fight(self, inter):
        data = inter.bot.fights
        msg = ""
        
        for i in data:
            name = str(data[i].author)
            since = f"<t:{data[i].time}:T>"
            msg += f"**Name**: {name}\n**Playing Since**:{since}\n"

        embed = disnake.Embed(
            title="list of people inside the fight flag",
            description=msg
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/900274624594575361/928703846476288120/IMG_0370.png"
        )
        await inter.send(embed=embed)

    @commands.slash_command()
    @commands.is_owner()
    async def in_shop(self, inter):
        data = inter.bot.shops
        msg = ""

        for i in data:
            name = str(data[i].author)
            since = f"<t:{data[i].time}:T>"
            msg += f"**Name**: {name}\n**Playing Since**:{since}\n"

        embed = disnake.Embed(
            title="list of people inside the shop flag",
            description=msg
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/900274624594575361/928703846476288120/IMG_0370.png"
        )
        await inter.send(embed=embed)

    @commands.slash_command()
    @commands.is_owner()
    async def vanish(self, inter, user: disnake.User = None):
        if user is None:
            return
        self.bot.players.delete_one({"_id": user.id})
        await inter.send("Done")

    @commands.slash_command(name="hallo", guilds_ids=[817437132397871135])
    async def greetings(self, inter):
        await inter.send("wuddap")

def setup(bot):
    bot.add_cog(Developer_Tools(bot))
