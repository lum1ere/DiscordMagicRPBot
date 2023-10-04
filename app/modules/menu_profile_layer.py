import discord
from discord import ui
from app.database import db_queries as dq
from app.modules.standart_modules import BackButton
from app.modules.embeds import ProfileLayerEmbed
from app.objects import User
from app.utils import accessors
from app.modules.commands import log as lg
from app.modules.profile import ProfileModal
from app.modules.profile import ProfileExtraModal


class ProfileLayer(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = ProfileLayerEmbed
        self.back_btn = BackButton(self, self.embed(target))

    @ui.button(label="Основной профильㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, emoji="📖")
    async def mainProfile(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()

        @accessors.target_can_change_character(self.target)
        async def _callback(**kwargs):
            modal = await ProfileModal.create(self.target)
            await interaction.response.send_modal(modal)

        await _callback(interaction=interaction)

    @ui.button(label="Дополнительный профиль", style=discord.ButtonStyle.grey, emoji="📝")
    async def extraProfile(self, interacion: discord.Interaction, btn):
        self.target = await self.target.update()

        @accessors.target_can_change_character(self.target)
        async def _callback(**kwargs):
            modal = ProfileExtraModal(self.target)
            await interacion.response.send_modal(modal)

        await _callback(interaction=interacion)