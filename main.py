import os
import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

HORA_MESSAGE_ID = None
HORARIOS_CHANNEL_NAME = "horarios"
DATA_FILE = "horarios.json"

EMOJIS = {
    "🌅": "mañana",
    "🌇": "tarde",
    "🌙": "noche"
}

# ------------------ STORAGE ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"mañana": [], "tarde": [], "noche": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ------------------ EMBED TABLE ------------------

def build_message():
    def format_list(lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    return (
        "🗓️ **HORARIOS DE QUEDADA**\n\n"
        f"🌅 **Mañana**\n{format_list(data['mañana'])}\n\n"
        f"🌇 **Tarde**\n{format_list(data['tarde'])}\n\n"
        f"🌙 **Noche**\n{format_list(data['noche'])}"
    )

# ------------------ BOT ------------------

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def crear_horarios(ctx):
    global HORA_MESSAGE_ID

    if ctx.channel.name != HORARIOS_CHANNEL_NAME:
        await ctx.send("Usa este comando en #horarios")
        return

    msg = await ctx.send(build_message())

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

    if reaction.emoji not in EMOJIS:
        return

    slot = EMOJIS[reaction.emoji]

    # evitar duplicados
    for k in data:
        if user.name in data[k]:
            data[k].remove(user.name)

    data[slot].append(user.name)
    save_data(data)

    await reaction.message.edit(content=build_message())


@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if HORA_MESSAGE_ID is None:
        return

    if reaction.message.id != HORA_MESSAGE_ID:
        return

    if reaction.emoji not in EMOJIS:
        return

    slot = EMOJIS[reaction.emoji]

    if user.name in data[slot]:
        data[slot].remove(user.name)
        save_data(data)

    await reaction.message.edit(content=build_message())


bot.run(os.environ["TOKEN"])
@bot.command()
async def horarios(ctx):
    def format_list(lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    msg = (
        "🗓️ **HORARIOS ACTUALES**\n\n"
        f"🌅 **Mañana**\n{format_list(data['mañana'])}\n\n"
        f"🌇 **Tarde**\n{format_list(data['tarde'])}\n\n"
        f"🌙 **Noche**\n{format_list(data['noche'])}"
    )

    await ctx.send(msg)
