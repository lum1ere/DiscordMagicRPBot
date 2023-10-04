import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds
from app.utils import accessors
from app.modules.commands import log


class ProfileChangingBlockView(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.ProfileLockSwitchEmbed(target)
        if target.active_character.can_edit_profile == "Да":
            self.switch.label = "ㅤЗаблокироватьㅤ"
            self.switch.style = discord.ButtonStyle.danger
            self.switch.emoji = "⚠️"
        else:
            self.switch.label = "ㅤРазблокироватьㅤ"
            self.switch.style = discord.ButtonStyle.green
            self.switch.emoji = "✅"

    @ui.button(label="None", style=discord.ButtonStyle.green, row=0)
    async def switch(self, interaction: discord.Interaction, button: discord.Button):
        await dq.switchProfileBlock(target=self.target)
        self.target.active_character = await self.target.active_character.update()
        if self.target.active_character.can_edit_profile == "Да":
            self.switch.label = "ㅤЗаблокироватьㅤ"
            self.switch.emoji = "⚠️"
            self.switch.style = discord.ButtonStyle.danger
        else:
            self.switch.label = "ㅤРазблокироватьㅤ"
            self.switch.style = discord.ButtonStyle.green
            self.switch.emoji = "✅"

        await interaction.response.edit_message(view=self, embed=await self.embed.update())
        await log(self.target, "switch_p_block", f"Профиль персонажа {self.target.active_character.name} сменил статус блокировки на {self.target.active_character.can_edit_profile}", interaction)



