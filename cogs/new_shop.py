import disnake
from disnake.ext import commands, components
from disnake.ui import Button, ActionRow
from disnake import ButtonStyle

from utility import loader


class ShopMenu:
    def __init__(
            self,
            bot,
            inter,
            author,
            msg,
            channel,
            data
    ):
        self.bot = bot
        self.inter = inter
        self.author = author
        self.msg = msg
        self.channel = channel
        self.edit = msg.edit
        self.data = data

    async def menu(self):
        comps = [
            Button(
                label="Buy",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="buy",
                    uid=str(self.author.id)
                ),
                style=ButtonStyle.green
            ),
            Button(
                label="Talk",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="talk",
                    uid=str(self.author.id)
                )
            ),
            Button(
                label="Sell",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="sell",
                    uid=str(self.author.id)
                )
            ),
            Button(
                label="End",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="end",
                    uid=str(self.author.id)
                ),
                style=ButtonStyle.red
            )
        ]
        embed = disnake.Embed(
            title="Welcome to the shop",
            description="Buy anything you need",
            color=disnake.Color.random()
        )
        embed.set_thumbnail(url=self.data["image"])

        await self.edit(embed=embed, components=[comps])

    async def buy(self):
        await self.edit(content="This is buying menu")

    async def talk(self):
        await self.edit(content="This is talking menu")

    async def sell(self):
        await self.edit(content="This is selling menu")

    async def end(self):
        await self.edit(content="This is ending quote", components=[])
        del self.bot.shops[str(self.author.id)]


class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.shops = {}

    @commands.command(aliases=[])
    async def new_shop(self, inter):

        await loader.create_player_info(inter, inter.author)
        info = await self.bot.players.find_one({"_id": inter.author.id})

        location = info["location"]
        lista = []
        for i in inter.bot.shopping[location]:
            lista.append(
                Button(
                    label=i.title(),
                custom_id=ShopCog.shop_selector_listener.build_custom_id(
                    shop=i,
                    loc=location,
                    uid=str(inter.author.id)
                )
                )
            )

        await inter.send("Select a Shop", components=[lista])

    @components.button_listener()
    async def shop_listener(self, inter: disnake.MessageInteraction, action: str, uid: str) -> None:
        if str(inter.author.id) != uid:
            return await inter.send("This is not yours kiddo!", ephemeral=True)

        # noinspection PyUnresolvedReferences
        await getattr(inter.bot.shops[uid], action)()

    @components.button_listener()
    async def shop_selector_listener(self, inter: disnake.MessageInteraction, shop: str, loc: str, uid: str) -> None:
        if str(inter.author.id) != uid:
            return await inter.send("This is not yours kiddo!", ephemeral=True)

        data = inter.bot.shopping[loc][shop]

        try:
            await inter.response.defer()
        except:
            pass

        msg = await inter.original_message()
        shop_obj = ShopMenu(inter.bot, inter, inter.author, msg, inter.channel, data)
        inter.bot.shops[str(inter.author.id)] = shop_obj
        await shop_obj.menu()


def setup(bot):
    bot.add_cog(ShopCog(bot))
