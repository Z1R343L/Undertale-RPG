import disnake
import humanize
from disnake.ext import commands

from utility.utils import get_all_funcs

class Leaderboard(commands.Cog):
    """Leaderboard and a developer tool for fixture"""

    def __init__(self, bot):
        self.bot = bot
        self.cmds = get_all_funcs(self)

    @commands.slash_command()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def leaderboard(self, inter, lb: str = "gold"):
        """see who's on the lead on gold amount"""

        if lb not in ["gold", "resets", "kills", "deaths", "spares"] or None:
            embed = disnake.Embed(
                title=f"There is no such leaderboard as {lb}",
                description=(
                    "You can only choose from the following leaderboards:\n\n"
                    "**gold, resets, kills, deaths, spares**."
                ),
                color=disnake.Color.red()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/900274624594575361/974933965356019772/trophy.png")
            inter.command.reset_cooldown(inter)
            return await inter.send(embed=embed)

        data = self.bot.players.find().limit(10).sort(lb, -1)
        users = []
        async for raw in data:
            users.append(raw)

        users.sort(key=lambda user: user[lb], reverse=True)

        output = [""]
        for i, user in enumerate(users, 1):
            player = await self.bot.fetch_user(user['_id'])
            if i == 1:
                i = ":medal:"
            if i == 2:
                i = ":second_place:"
            if i == 3:
                i = ":third_place:"

            if len(str(player)) >= 24:
                player = str(player)[:-10]

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
        embed.set_image(
            url="https://media.discordapp.net/attachments/900274624594575361/974936472199249970/lb_image.png"
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/900274624594575361/974933965356019772/trophy.png"
        )
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
