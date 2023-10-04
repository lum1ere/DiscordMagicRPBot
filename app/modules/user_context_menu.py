import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds, ctx_show_profile, ctx_show_timeline, gm_context_menu
from app.utils import accessors
from app.modules.standart_modules import BackButton
from app.modules.commands import log as lg


class UserMenu(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.UserMenuEmbed(target=target)
        self.back_btn = BackButton(self, self.embed)

    @ui.button(label="Посмотреть анкетуㅤㅤ", style=discord.ButtonStyle.grey, emoji="👁️")
    async def showProfile(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = await ctx_show_profile.ProfileViewer.create(target=self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(
                content=self.target.active_character.profile.short_desc,
                view=view, embed=None)
            await lg(self.target, "show_user_profile", f"{interaction.user.name} смотрит анкету персонажа {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)

    @ui.button(label="Посмотреть таймлайн", style=discord.ButtonStyle.grey, emoji="🕓")
    async def showTimeline(self, interaction: discord.Interaction, button: discord.Button):
        @accessors.target_has_character(self.target)
        async def callback(**kwargs):
            self.target = await self.target.update()
            view = await ctx_show_timeline.TimeLineView.create(target=self.target)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(view=view, embed=view.embed)
            await lg(self.target, "show_user_profile", f"{interaction.user.name} смотрит таймлайн персонажа {self.target.active_character.webhook.name}!", interaction)


        await callback(interaction=interaction)








