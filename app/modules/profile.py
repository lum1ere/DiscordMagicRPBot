import discord, aiosqlite
from discord import ui
from app.objects import User, Character, Profile
from app.modules.embeds import ProfileWasSuccessfullyChangedEmbed
from app.utils import accessors
from app.modules.commands import log


class ProfileModal(ui.Modal):
    @classmethod
    async def create(cls, user: User):
        character = user.active_character
        self = ProfileModal(title=f"Профиль персонажа {character.webhook.name}")
        self.character = character
        profile = character.profile
        self.add_item(ui.TextInput(label="Краткая информация о сосуде", max_length=2000, required=True, default=profile.short_desc, style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Лист 1", max_length=2000, required=False, default=profile.field_1, style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Лист 2", max_length=2000, required=False, default=profile.field_2, style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Лист 3", max_length=2000, required=False, default=profile.field_3, style=discord.TextStyle.long))
        #self.add_item(ui.TextInput(label="Лист 4", max_length=2000, required=False, default=profile.extra_1, style=discord.TextStyle.long))

        async def callback(interaction: discord.Interaction) -> None:
            short = str(self.children[0])
            field_1 = str(self.children[1])
            field_2 = str(self.children[2])
            field_3 = str(self.children[3])

            undefended_fields = [field_1, field_2, field_3]
            for index, field in enumerate(undefended_fields):
                if not field:
                    undefended_fields[index] = "-"

            await user.active_character.profileCommit(args=[short, *undefended_fields])
            await interaction.response.send_message(
                ephemeral=True,
                embed=ProfileWasSuccessfullyChangedEmbed(character.name)
                                                    )
            await log(user, "profile_changed", f"Анкета персонажа {self.character.webhook.name} изменена", interaction)

        self.on_submit = callback
        return self


class ProfileExtraModal(ui.Modal):
    def __init__(self, target: User):
        self.target = target
        profile = target.active_character.profile
        super().__init__(title=f"Дополнительные листы профиля {self.target.active_character.webhook.name}")

        self.add_item(ui.TextInput(label="Доп. Лист 1",
                                   max_length=2000, required=False,
                                   default=profile.extra_1,
                                   style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Доп. Лист 2",
                                   max_length=2000, required=False,
                                   default=profile.extra_2,
                                   style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Доп. Лист 3",
                                   max_length=2000, required=False,
                                   default=profile.extra_3,
                                   style=discord.TextStyle.long))
        self.add_item(ui.TextInput(label="Доп. Лист 4",
                                   max_length=2000, required=False,
                                   default=profile.extra_4,
                                   style=discord.TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        extra_1 = str(self.children[0])
        extra_2 = str(self.children[1])
        extra_3 = str(self.children[2])
        extra_4 = str(self.children[3])
        undefended_fields = [extra_1, extra_2, extra_3, extra_4]
        for index, field in enumerate(undefended_fields):
            if not field:
                undefended_fields[index] = "-"

        await self.target.active_character.profileExtraCommit(args=[*undefended_fields])

        await interaction.response.send_message(
            ephemeral=True,
            embed=ProfileWasSuccessfullyChangedEmbed(self.target.active_character.webhook.name)
        )
        await log(self.target, "profile_changed", f"Анкета персонажа {self.target.active_character.name} изменена", interaction)

