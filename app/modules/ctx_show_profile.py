import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds


class ProfileViewer(ui.View):
    @classmethod
    async def create(cls, target: User, page=1):
        self = ui.View(timeout=None)
        self.target = target
        self.page = 1
        profile = target.active_character.profile
        profile_fields = [profile.short_desc, profile.field_1, profile.field_2, profile.field_3, profile.extra_1, profile.extra_2, profile.extra_3, profile.extra_4]

        accessible_fields = []

        for index, field in enumerate(profile_fields):
            if field != "-" or field != "-":
                accessible_fields.append(field)

        if not accessible_fields:
            self.content = "Похоже, что здесь пока что ничего нет..."
            return self
        self.fields = accessible_fields
        self.max_page = len(accessible_fields)
        self.add_item(LeftButton(self))
        self.add_item(RightButton(self))

        async def check():
            if self.page == 1:
                self.children[0].disabled = True
            elif self.page == self.max_page:
                self.children[1].disabled = True
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            if self.page > 1:
                self.children[0].disabled = False
            fields = self.fields
            self.content = fields[self.page - 1]
            return self

        self.check = check

        async def update():
            return await ProfileViewer.create(self.target)

        self.update = update

        return self


class RightButton(ui.Button):
    def __init__(self, parent: ui.View):
        super().__init__(emoji="➡️", style=discord.ButtonStyle.grey, row=1)
        self.parent = parent
        if parent.page == self.parent.max_page:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.parent.page < self.parent.max_page:
            self.parent.page += 1
        await self.parent.check()
        await interaction.response.edit_message(content=self.parent.content, view=self.parent)


class LeftButton(ui.Button):
    def __init__(self, parent: ui.View):
        super().__init__(emoji="⬅️", style=discord.ButtonStyle.grey, row=1)
        self.parent = parent
        if parent.page == 1:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.parent.page > 1:
            self.parent.page -= 1
        await self.parent.check()
        await interaction.response.edit_message(content=self.parent.content, view=self.parent)

