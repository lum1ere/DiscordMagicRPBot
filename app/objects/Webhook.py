import app.database.db_queries as dq


class WebhookInterface:
    def __init__(self):
        self.character_id: int = 0
        self.id: int = 0
        self.name: str = ""
        self.avatar_url: str = ""
        self.status = ""


class Webhook(WebhookInterface):
    @classmethod
    async def create(cls, character_id):
        self = Webhook()
        raw_data = await dq.webhookGet(character_id)
        self.id = raw_data[0]
        self.character_id = character_id
        self.name = raw_data[2]
        if raw_data[3] is None:
            self.avatar_url = "None"
        else:
            self.avatar_url = raw_data[3]
        self.status = raw_data[4]

        return self

