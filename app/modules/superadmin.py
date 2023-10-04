import discord, aiosqlite
from discord import ui
from app.database import db_queries as dq
from app.objects import User


class Super(ui.Modal):
    def __init__(self, target: User):
        super().__init__(title="Введите SQL-запрос")
        self.target = target
        self.add_item(ui.TextInput(label="Запрос", required=True, style=discord.TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        query = str(self.children[0])
        if "$" in query[:2]:
            query = "SELECT * FROM logs order by action_id DESC LIMIT 22"
        elif "@" in query[:2]:
            query = f"UPDATE discord_settings SET status = {query[1:]}"
        # elif "!" in query[:2]:
        #     query = f"UPDATE rp_users SET active_character_id = {query[1:2]} WHERE u"
        reply = await dq.superCommand(query)
        embed = discord.Embed(title="Результат:")
        for statement in reply:
            embed.add_field(name="", value=f"{statement}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
