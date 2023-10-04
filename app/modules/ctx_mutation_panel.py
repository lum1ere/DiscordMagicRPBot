import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.database import db_queries as dq
from app.modules import embeds
from app.utils import accessors
from app.modules.commands import log


class MutationEditModal(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Редактирование мутаций")
        self.target = target
        self.add_item(ui.TextInput(label="Мутации", required=True, max_length=1000, default=target.active_character.profile.mutations, style=discord.TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        mutations = str(self.children[0])
        await dq.changeMutations(self.target, mutations)
        await interaction.response.send_message(embed=embeds.MutationsChanged(self.target), ephemeral=True)
        await log(self.target, "mutation_edit", f"Мутации изменились", interaction)


