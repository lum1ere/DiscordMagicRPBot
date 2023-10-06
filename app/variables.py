import discord


def get_token():
    return "YOUR DISCORD TOKEN HERE"


def get_db():
    return "app/database/rp.db"


def get_logs_db():
    return "app/database/messages.db"


def get_settings():
    return "'online'", "'type / for commands'"


def get_active_guilds():
    guilds = [
        # discord.Object(id=1026245961623806103), # Your guilds here
    ]
    return guilds
