import disnake
from disnake.ext import commands


class Developer_Tools(commands.Cog):
    """A Module for the developer tools"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.is_owner()
    async def spit(self, inter, member: disnake.User = None):
        member = member or inter.author
        info = await inter.bot.players.find_one({"_id": member.id})
        await inter.send(info)

    @commands.slash_command()
    @commands.is_owner()
    async def Fix(self, inter):
        """Fix, duh?"""
        await inter.send("Fixing")
        data = self.bot.players.find()
        self.bot.fights = []

        await inter.send("Done!")

    @commands.slash_command()
    @commands.is_owner()
    async def debug_dat(self, inter, user: disnake.User = None):
        if user is None:
            return
        data = await self.bot.players.find_one({"_id": user.id})
        embed = disnake.Embed()
        for key in data:
            embed.add_field(name=key, value=data[key])
        await inter.send(embed=embed)

    @commands.slash_command()
    @commands.is_owner()
    async def in_fight(self, inter):
        data = inter.bot.fights

        embed = disnake.Embed(
            title="list of people inside the fight flag",
            description=data
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

def setup(bot):
    bot.add_cog(Developer_Tools(bot))
