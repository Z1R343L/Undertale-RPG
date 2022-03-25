import disnake
from disnake.ext import commands


class Developer_Tools(commands.Cog):
    """A Module for the developer tools"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def spit(self, ctx, member: disnake.User = None):
        member = member or ctx.author
        info = await ctx.bot.players.find_one({"_id": member.id})
        await ctx.send(info)

    @commands.command(aliases=["disable", "global", "shut"])
    @commands.is_owner()
    async def Disable(self, ctx):
        if self.bot.ENABLED:
            self.bot.ENABLED = False
            await ctx.send("Disabled")
        else:
            self.bot.ENABLED = True
            await ctx.send("Enabled")

    @commands.command(aliases=["fix"])
    @commands.is_owner()
    async def Fix(self, ctx):
        """Fix, duh?"""
        await ctx.send("Fixing")
        data = self.bot.players.find()
        async for info in data:
            if info["fighting"]:
                info["fighting"] = False
                info["selected_monster"] = None
                await self.bot.players.update_one({"_id": info["_id"]}, {"$set": info})

        await ctx.send("Done!")

    @commands.command()
    @commands.is_owner()
    async def debug_dat(self, ctx, user: disnake.User = None):
        if user is None:
            return
        data = await self.bot.players.find_one({"_id": user.id})
        embed = disnake.Embed()
        for key in data:
            embed.add_field(name=key, value=data[key])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def in_fight(self, ctx):
        data = ctx.bot.fights

        embed = disnake.Embed(
            title="list of people inside the fight flag",
            description=data
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/900274624594575361/928703846476288120/IMG_0370.png"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def vanish(self, ctx, user: disnake.User = None):
        if user is None:
            return
        self.bot.players.delete_one({"_id": user.id})
        await ctx.send("Done")

    @commands.command()
    @commands.is_owner()
    async def database_count(self, ctx):
        dat = self.bot.players.find()
        i = 0
        async for _ in dat:
            i += 1

        await ctx.send(f"{i} Users Registered So far!")

    @commands.command()
    @commands.is_owner()
    async def clearinv(self, ctx):
        author = ctx.author
        await ctx.send("Warning!, Your inventory will be cleared!. proceed?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check, timeout=100)
        if msg.content.lower() == "no":
            await ctx.send("Aborted")
            return

        elif msg.content.lower() == "yes":
            info = await self.bot.players.find_one({"_id": author.id})
            info["inventory"] = []
            await self.bot.players.update_one({"_id": author.id}, {"$set": info})

            await ctx.send("inventory cleared!")

def setup(bot):
    bot.add_cog(Developer_Tools(bot))
