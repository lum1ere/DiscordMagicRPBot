import aiosqlite
from app.variables import get_db
import app.database.db_queries as dq
import discord
from discord import ui
from app.utils.accessors import is_registered, log
from app.objects import User, Character, Core, Ci, Ai
from app.modules import embeds


class CoreSelector(ui.Select):
    def __init__(self, character: Ci):
        super().__init__(placeholder="Выберите тип ядра", max_values=1, min_values=1)
        self.add_option(label="Стандартный", description="1 Высокий 2 Средних", value="Стандартный")
        self.add_option(label="Дуальный", description="2 Высоких", value="Дуальный")
        self.add_option(label="Аспект", description="1 Высший", value="Аспект")
        self.character = character

    async def callback(self, interaction: discord.Interaction):
        option = str(self.values[0])
        self.character.core.core_type = option
        item = await ElementSelector.create(character=self.character)
        await interaction.response.edit_message(view=ui.View(timeout=None).add_item(item))


class ElementSelector(ui.Select):
    @classmethod
    async def create(cls, character: Ci, page=1):
        self = ui.Select(placeholder="Выберите элемент", min_values=1, max_values=1)
        options: list = []
        self.page = page
        self.character = character
        self.level = await dq.getNeededAffinityLevel(character.core)

        if page == 1:
            options = (await dq.getAllElements())[:15]
        if page == 2:
            self.add_option(label="Вернуться назад", value="goback")
            options = (await dq.getAllElements())[15:]
            for index, opt in enumerate(options):
                if opt[1] == 'базовый':
                    options.pop(index)

        [self.add_option(label=f"{option[1].capitalize()}", description=self.level, value=option[0]) for option in options]

        if page == 1:
            self.add_option(label="Посмотреть больше", value="gonext")

        async def _callback(interaction: discord.Interaction) -> None:
            selected_value = self.values[0]
            if selected_value == "gonext":
                item = await ElementSelector.create(character=self.character, page=2)
                await interaction.response.edit_message(view=ui.View(timeout=None).add_item(item))
            elif selected_value == "goback":
                item = await ElementSelector.create(character=self.character, page=1)
                await interaction.response.edit_message(view=ui.View(timeout=None).add_item(item))
            else:
                element_id = int(selected_value)
                affinity = Ai()
                affinity.affinity_element_id = element_id
                affinity.affinity_level_name = self.level

                flag = True
                for aff in self.character.core.affinities:
                    if aff.affinity_element_id == affinity.affinity_element_id:
                        flag = False
                if flag:
                    self.character.core.affinities.append(affinity)

                next_level = await dq.getNeededAffinityLevel(self.character.core)
                if next_level != "STOP":
                    item = await ElementSelector.create(character=self.character, page=self.page)
                    await interaction.response.edit_message(view=ui.View(timeout=None).add_item(item))
                else:
                    await self.character.push(interaction.user.id)
                    await interaction.response.edit_message(view=None, embed=embeds.RegistrationFinishedEmbed())
        self.callback = _callback
        return self


class RegistrationModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Регистрация")
        self.add_item(ui.TextInput(label="Введите имя персонажа"))
        self.character = Ci()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        @is_registered
        @log(None, "reg", f"Персонаж создан")
        async def callback(**kwargs):
            self.character.name = str(self.children[0]).capitalize()
            await interaction.response.send_message(ephemeral=True, view=ui.View(timeout=None).add_item(CoreSelector(character=self.character)))
        await callback(interaction=interaction)


