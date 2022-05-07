import disnake
from disnake.ext import commands, components
from disnake.ui import button, ActionRow


class ShopMenu:
    def __init__(
            self,
            bot,
            inter,
            author,
            msg,
            channel
    ):
        self.bot = bot
        self.inter = inter
        self.author = author
        self.msg = msg
        self.channel = channel
        self.edit = msg.edit
        self.data = {}

    async def menu(self):
        comps = [
            button(
                label="Buy",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="buy",
                    uid=str(self.author.id)
                )
            ),
            button(
                label="Talk",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="talk",
                    uid=str(self.author.id)
                )
            ),
            button(
                label="Sell",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="sell",
                    uid=str(self.author.id)
                )
            ),
            button(
                label="End",
                custom_id=ShopCog.shop_listener.build_custom_id(
                    action="end",
                    uid=str(self.author.id)
                )
            )
        ]
        await self.edit(content="This is menu", components=[comps])

    async def buy(self):
        await self.edit(content="This is buying menu")

    async def talk(self):
        await self.edit(content="This is talking menu")

    async def sell(self):
        await self.edit(content="This is selling menu")

    async def end(self):
        await self.edit(content="This is ending quote")
        del self


class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.shops = {}

    @commands.command(aliases=[])
    async def new_shop(self, inter):
        msg = await inter.send("Shop initialised")
        shop_obj = ShopMenu(inter.bot, inter, inter.author, msg, inter.channel)
        self.bot.shops[str(inter.author)] = shop_obj
        await shop_obj.menu()

    @components.button_listener()
    async def shop_listener(self, inter: disnake.MessageInteraction, action: str, uid: str) -> None:
        if str(inter.author.id) != uid:
            return await inter.send("This is not yours kiddo!", ephemeral=True)

        await getattr(self.bot.shops[uid], action)()


def setup(bot):
    bot.add_cog(ShopCog(bot))
