import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds
from app.modules.commands import log


class CharactersChangingBlockView(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.CharacterChangeLockSwitchEmbed(target)
        if target.can_change == "Да":
            self.switch.label = "Заблокировать"
            self.switch.style = discord.ButtonStyle.danger
            self.switch.emoji = "⚠️"
        else:
            self.switch.label = "Разблокировать"
            self.switch.style = discord.ButtonStyle.green
            self.switch.emoji = "✅"

    @ui.button(label="None", style=discord.ButtonStyle.green, row=0)
    async def switch(self, interaction: discord.Interaction, btn):
        await dq.switchCharactersChangingBlock(target=self.target)
        self.target = await self.target.update()
        if self.target.can_change == "Да":
            self.switch.label = "Заблокировать"
            self.switch.style = discord.ButtonStyle.danger
            self.switch.emoji = "⚠️"
        else:
            self.switch.label = "Разблокировать"
            self.switch.style = discord.ButtonStyle.green
            self.switch.emoji = "✅"

        await interaction.response.edit_message(view=self, embed=await self.embed.update())
        await log(self.target, "switch_cc_block", f"Блокировка изменена на {self.target.can_change}", interaction)

