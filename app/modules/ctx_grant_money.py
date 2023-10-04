import discord
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds
from app.objects import User
from app.utils import accessors
from app.modules.commands import log


class EditMoneyModal(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Редактирование денег")
        self.target = target
        self.add_item(ui.TextInput(label="Деньги", required=True, default=str(target.active_character.money)))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        money = str(self.children[0])
        await dq.grantMoney(self.target, money)
        self.target = await self.target.update()
        await interaction.response.edit_message(embed=embeds.InventoryMenuEmbed(self.target))
        await log(self.target, "edit_money", f"Изменение денег с {self.target.active_character.money} на {str(self.children[0])}", interaction)
