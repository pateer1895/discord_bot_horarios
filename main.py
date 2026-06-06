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

# estructura: { "mañana": set(), "tarde": set(), "noche": set() }
horarios = {
    "🌅": set(),
    "🌇": set(),
    "🌙": set()
}


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def crear_horarios(ctx):
    global HORA_MESSAGE_ID

    if ctx.channel.name != HORARIOS_CHANNEL_NAME:
        await ctx.send("Este comando solo se usa en #horarios")
        return

    msg = await ctx.send(
        "🗓️ **Horarios de quedada**\n\n"
        "Reacciona según disponibilidad:\n\n"
        "🌅 Mañana\n"
        "🌇 Tarde\n"
        "🌙 Noche"
    )

    await msg.add_reaction("🌅")
    await msg.add_reaction("🌇")
    await msg.add_reaction("🌙")

    HORA_MESSAGE_ID = msg.id


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if HORA_MESSAGE_ID is None:
        return

    if reaction.message.id != HORA_MESSAGE_ID:
        return

    emoji = reaction.emoji

    if emoji in horarios:
        horarios[emoji].add(user.name)

        print("----- HORARIOS -----")
        print("🌅 Mañana:", horarios["🌅"])
        print("🌇 Tarde:", horarios["🌇"])
        print("🌙 Noche:", horarios["🌙"])


@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if HORA_MESSAGE_ID is None:
        return

    if reaction.message.id != HORA_MESSAGE_ID:
        return

    emoji = reaction.emoji

    if emoji in horarios and user.name in horarios[emoji]:
        horarios[emoji].remove(user.name)


bot.run(os.environ["TOKEN"])
