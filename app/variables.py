import discord


def get_token():
    return "MTA1NzcyMjAzMTAyNzc5ODEzNg.G7ZIRc.zWuCosDg7iphLKh-B74QKBD1uiDrOSqCoTXsTo"


def get_db():
    return "app/database/rp.db"


def get_logs_db():
    return "app/database/messages.db"


def get_settings():
    return "'online'", "'type / for commands'"


def get_active_guilds():
    guilds = [
        discord.Object(id=1026245961623806103),
        #discord.Object(id=1089680525737861130)
    ]
    return guilds