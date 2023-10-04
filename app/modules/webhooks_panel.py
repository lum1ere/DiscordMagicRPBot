import discord
from discord import ui
from app.database import db_queries as dq
from app.objects import User
from app.modules import embeds
from app.modules.commands import log as lg


class WebhookMenu(ui.View):
    def __init__(self, target: User):
        super().__init__(timeout=None)
        self.target = target
        self.embed = embeds.WebhookMenuEmbed(self.target)
        self.embed_template = embeds.WebhookMenuEmbed
        self.webhookButtonUpdate()

    @ui.button(label="Редактировать Вебхук", style=discord.ButtonStyle.grey, emoji="📩")
    async def changeWebhook(self, interaction: discord.Interaction, btn):
        modal = WebhookEditModal(self.target)
        modal.embed_template = self.embed_template
        await interaction.response.send_modal(modal)
        await lg(self.target, "edit_webhook", f"{interaction.user.name} редактирует свой вебхук!", interaction)

    @ui.button(label="Запустить Вебхукㅤㅤ", style=discord.ButtonStyle.blurple, emoji="📨")
    async def startWebhook(self, interaction: discord.Interaction, btn):
        self.target = await self.target.update()
        webhook = self.target.active_character.webhook
        if webhook.status == "activated":
            webhook.status = "deactivated"
        else:
            webhook.status = "activated"
        await dq.webhookChange(self.target, webhook)
        self.webhookButtonUpdate()
        await interaction.response.edit_message(embed=self.embed_template(self.target), view=self)
        await lg(self.target, "start_webhook", f"{interaction.user.name} останавливает / запускает свой вебхук!", interaction)

    def webhookButtonUpdate(self):
        webhook = self.target.active_character.webhook
        if webhook.status == "deactivated":
            self.startWebhook.label = "Запустить Вебхукㅤㅤ"
            self.startWebhook.style = discord.ButtonStyle.green
            self.startWebhook.emoji = "📨"
        else:
            self.startWebhook.label = "Остановить Вебхукㅤㅤ"
            self.startWebhook.style = discord.ButtonStyle.danger
            self.startWebhook.emoji = "⚠️"


class WebhookEditModal(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Редактирование вебхука")
        self.embed_template = None
        self.target = target
        self.webhook = target.active_character.webhook
        self.add_item(ui.TextInput(label="Псевдоним", max_length=70, required=True, default=self.webhook.name))
        self.add_item(ui.TextInput(label="Аватар", max_length=200, required=False, default=self.webhook.avatar_url))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        name = str(self.children[0])
        avatar = str(self.children[1])
        if not avatar:
            avatar = None
        self.webhook.name = name
        self.webhook.avatar_url = avatar
        await dq.webhookChange(self.target, self.webhook)
        await interaction.response.edit_message(embed=self.embed_template(self.target))
