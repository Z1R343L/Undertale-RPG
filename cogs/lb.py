import disnake
import humanize
from disnake.ext import commands


class Leaderboard(commands.Cog):
    """Leaderboard and a developer tool for fixture"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lb"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def leaderboard(self, ctx, arg: str = "level"):
        """see who's on the lead on gold amount"""

        data = self.bot.players.find().limit(10).sort(arg, -1)
        users = []
        async for raw in data:
            users.append(raw)

        users.sort(key=lambda user: user[arg], reverse=True)

        output = [""]
        for i, user in enumerate(users, 1):
            output.append(
                f"{i}. {user['name']}: {humanize.intcomma(int(user[arg]))} {arg}"
            )
            if i == 10:
                break
        output.append("")
        result = "\n".join(output)
        embed = disnake.Embed(
            title=f"{arg} Leaderboard:",
            description=f"**{result}**",
            color=disnake.Colour.gold(),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
