import discord, aiosqlite
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds, ctx_grant_money
from app.objects import User
from app.objects.Item import ItemInterface
from app.modules.standart_modules import BackButton
from math import ceil
from app.utils import accessors
from app.modules.commands import log as lg
import asyncio


class InventoryView(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.InventoryMenuEmbed(target)
        self.back_btn = BackButton(menu_view=self, menu_embed=self.embed)

    @ui.button(label="Открыть инвентарьㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, emoji="📦")
    async def openInventory(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()
        item = ItemSelector(self.target)
        item.back_btn = self.back_btn
        view = ui.View(timeout=None).add_item(item)
        view.add_item(self.back_btn)
        await interaction.response.edit_message(view=view)

    @ui.button(label="Создать предметㅤㅤㅤㅤㅤ", style=discord.ButtonStyle.grey, emoji="🌀")
    async def newItem(self, interaction: discord.Interaction, btn):
        await interaction.response.send_modal(CreateItemModal(self.target))
        await lg(self.target, "add_item", f"{interaction.user.name} добавляет предмет персонажу {self.target.active_character.webhook.name}!", interaction)

    @ui.button(label="Редактировать деньгиㅤㅤㅤ", style=discord.ButtonStyle.blurple, row=1, emoji="🪙")
    async def editMoney(self, interaction: discord.Interaction, button: discord.Button):
        async def callback(**kwargs):
            self.target = await self.target.update()
            modal = ctx_grant_money.EditMoneyModal(self.target)
            await interaction.response.send_modal(modal)
            await lg(self.target, "edit_money", f"{interaction.user.name} редактирует деньги персонажу {self.target.active_character.webhook.name}!", interaction)

        await callback(interaction=interaction)


class ItemSelector(ui.Select):
    def __init__(self, target: User, flag=""):
        super().__init__(placeholder="Выберите предмет", max_values=1, min_values=1)
        self.page = 1
        self.target = target
        self.embed = embeds.InventoryMenuEmbed(self.target)
        self.max_pages = ceil(len(target.active_character.inventory) / 5)
        self.items = target.active_character.inventory
        self.flag = flag
        self.add_option(label="Вывести всё", value="_all", emoji="🔁")
        [self.add_option(
            label=item.name[:50],
            description=item.desc[:90]+'...',
            value=item.id, emoji="🏷️") for item in self.items]

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        if option == "nextpage":
            if self.page != self.max_pages:
                self.page += 1
            await interaction.response.edit_message(embed=embeds.InventoryShowEmbed(self.target, page=self.page))
        elif option == "backpage":
            if self.page != 1:
                self.page -= 1
            await interaction.response.edit_message(embed=embeds.InventoryShowEmbed(self.target, page=self.page))
        elif option == "return":
            self.options.clear()
            self.add_option(label="Вывести всё", value="_all", emoji="🔁")
            [self.add_option(label=item.name, description=item.desc, value=item.id) for item in self.items]
            await interaction.response.edit_message(embed=embeds.InventoryMenuEmbed(self.target),
                                                    view=self.view)
        elif option == "_all":
            self.options.clear()
            self.add_option(label="Следующая страница", value="nextpage", emoji="➡️")
            self.add_option(label="Предыдущая страница", value="backpage", emoji="⬅️")
            self.add_option(label="Назад", value="return", emoji="↩️")
            self.placeholder = "Все предметы"
            await interaction.response.edit_message(embed=embeds.InventoryShowEmbed(self.target, page=self.page), view=self.view)

        else:
            option = int(option)
            _item = 0
            for item in self.items:
                if item.id == option:
                    _item = item

            if "nodelete" in self.flag:
                view = await self.regen(_item, flag="")
            else:
                view = await self.regen(_item, flag="delete")
            await interaction.response.edit_message(embed=embeds.InventorySingleShowEmbed(self.target, _item),
                                                    view=view)

    async def regen(self, _item, flag=""):
        view = ui.View(timeout=None)
        item = ItemSelector(self.target, self.flag)
        item.back_btn = self.back_btn
        item.placeholder = _item.name
        if "delete" in flag:
            dib = DeleteItem(_item, self.target, self.back_btn)
            view.add_item(dib)
        view.add_item(item)
        view.add_item(self.back_btn)

        return view


class CreateItemModal(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Создание предмета")
        self.target = target
        self.add_item(discord.ui.TextInput(label="Название предмета", max_length=100, required=True))
        self.add_item(discord.ui.TextInput(label="Описание", max_length=1000, required=True, style=discord.TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction):
        item = ItemInterface()
        item.name = str(self.children[0])
        item.desc = str(self.children[1])
        await dq.addItem(self.target, item)
        await interaction.response.edit_message(embed=embeds.InventoryMenuEmbed(self.target))
        await lg(self.target, "item_create", f"Создан предмет {str(self.children[0])} для персонажа {self.target.active_character.name}", interaction)


class DeleteItem(ui.Button):
    def __init__(self, item, target, back_btn):
        super().__init__(label="Удалить предметㅤㅤㅤ", style=discord.ButtonStyle.danger, row=2, emoji="⚠️")
        self.item = item
        self.target = target
        self.back_btn = back_btn
        self.pressed = 0

    async def callback(self, interaction: discord.Interaction):
        self.pressed += 1
        if self.pressed == 1:
            await interaction.response.send_message(ephemeral=True, embed=embeds.AreYouSure(self.target))
            await asyncio.sleep(5)
            self.pressed = 0
        if self.pressed == 2:
            self.target = await self.target.update()
            await dq.dropItem(self.item)
            self.target = await self.target.update()
            item = ItemSelector(self.target)
            view = ui.View(timeout=None).add_item(item)
            view.add_item(self.back_btn)
            await interaction.response.edit_message(embed=embeds.InventoryMenuEmbed(self.target), view=view)
            await log(self.target, "item_delete", f"Удаление предмета {self.item.name}", interaction)
