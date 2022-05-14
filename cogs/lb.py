import disnake
import humanize
from disnake.ext import commands


class Leaderboard(commands.Cog):
    """Leaderboard and a developer tool for fixture"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lb"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def leaderboard(self, ctx, lb: str = "level"):
        """see who's on the lead on gold amount"""

        if lb not in ["gold", "resets", "kills", "deaths", "spares"]:
            return

        data = self.bot.players.find().limit(10).sort(lb, -1)
        users = []
        async for raw in data:
            users.append(raw)

        users.sort(key=lambda user: user[lb], reverse=True)

        output = [""]
        for i, user in enumerate(users, 1):
            player = await self.bot.fetch_user(user['_id'])
            output.append(
                f"{i}. {str(player)}: {humanize.intcomma(int(user[lb]))} {lb}"
            )
            if i == 10:
                break
        output.append("")
        result = "\n".join(output)
        embed = disnake.Embed(
            title=f"{lb} Leaderboard:",
            description=f"**{result}**",
            color=disnake.Colour.gold(),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
