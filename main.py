import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

HORA_MESSAGE_ID = None
HORARIOS_CHANNEL_NAME = "horarios"


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")


@bot.command()
async def crear_horarios(ctx):
    global HORA_MESSAGE_ID

    if ctx.channel.name != HORARIOS_CHANNEL_NAME:
        await ctx.send("Este comando solo se usa en #horarios")
        return

    msg = await ctx.send(
        "🗓️ **Sistema de horarios**\n\n"
        "Reacciona:\n"
        "🟢 Disponible\n"
        "🔴 No disponible"
    )

    await msg.add_reaction("🟢")
    await msg.add_reaction("🔴")

    HORA_MESSAGE_ID = msg.id


@bot.event
async def on_reaction_add(reaction, user):
    global HORA_MESSAGE_ID

    if user.bot:
        return

    if HORA_MESSAGE_ID is None:
        return

    if reaction.message.id != HORA_MESSAGE_ID:
        return

    if reaction.emoji == "🟢":
        print(f"{user} está disponible")

    elif reaction.emoji == "🔴":
        print(f"{user} NO está disponible")


bot.run(os.environ["TOKEN"])
