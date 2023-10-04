import discord
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds
from app.objects import User
from app.utils import accessors
from app.modules.commands import log


class EditManaModal(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Редактирование маны")
        self.target = target
        self.add_item(ui.TextInput(label="Мана", required=True, default=str(target.active_character.mana)))
        self.add_item(ui.TextInput(label="Максимальный запас маны", required=True, default=str(target.active_character.manapool)))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        mana = float(str(self.children[0]))
        manapool = float(str(self.children[1]))
        await dq.changeManapoolAndMana(self.target, manapool, mana)
        await interaction.response.send_message(embed=embeds.ManaChanged(self.target), ephemeral=True)
        await log(self.target, "edit_mana", f"Изменение маны с {self.target.active_character.mana} на {float(str(self.children[0]))}", interaction)

