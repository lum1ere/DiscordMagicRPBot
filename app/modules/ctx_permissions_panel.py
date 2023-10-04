import discord
from discord import ui
from app.database import db_queries as dq
from app.modules import embeds
from app.objects import User
from app.utils import accessors
from app.modules.commands import log


class PermissionsSelector(ui.Select):
    @classmethod
    async def create(cls, target: User, author_id: int, menu_view: ui.View, menu_embed: discord.Embed):
        self = ui.Select(placeholder="Выберите роль", min_values=1, max_values=1)
        self.target = target
        self.embed = embeds.PermissionsManagementEmbed(target)
        permissions = await dq.allPermissions(user_id=author_id)
        current_permission = await dq.getAccessLevel(target.id)
        _permissions = {0: 'superadmin', 1: 'admin', 2: 'gm', 3: 'player', 4: 'noname'}
        current_permission_name = _permissions[current_permission]
        self.placeholder = current_permission_name
        [self.add_option(label=permission[1], value=permission[0]) for permission in permissions]

        async def _callback(interaction: discord.Interaction):
            option = int(self.values[0])
            await dq.changePermission(self.target, option)
            await interaction.response.edit_message(view=menu_view, embed=menu_embed)
            await log(self.target, "permission_change", f"Роль {target.name} сменилась на {option}", interaction)

        self.callback = _callback
        return self


