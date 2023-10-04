import discord, aiosqlite
from discord import ui
from app.objects import User
from app.database import db_queries as dq
from app.modules import embeds
from app.modules.commands import log


class CharacterChangeSelector(ui.Select):
    @classmethod
    async def create(cls, user: User):
        self = ui.Select(placeholder="Выберите персонажа")
        self.user = user
        accessible_characters = await dq.getCharactersOfUser(user=user)
        for character in accessible_characters[:10]:
            self.add_option(label=f"{character[1]}", value=character[0])

        async def _callback(interaction: discord.Interaction):
            option = int(self.values[0])
            await dq.changeActiveCharacterOfUser(user=self.user, character_id=option)
            self.user = await user.update()
            await interaction.response.edit_message(embed=self.back_embed(self.user), view=self.back_view(self.user))

        self.callback = _callback
        return self
