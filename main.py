print(">>> MAIN CARGADO CORRECTAMENTE <<<")

import os
import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "horarios.json"
MESSAGE_ID_FILE = "msgid.json"

# user_id -> ["mañana","tarde","noche"]
data = {}

MESSAGE_ID = None


# ---------------- PERSISTENCIA ----------------

def load_data():
    global data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_msg_id():
    global MESSAGE_ID
    try:
        with open(MESSAGE_ID_FILE, "r") as f:
            MESSAGE_ID = json.load(f)["id"]
    except:
        MESSAGE_ID = None

def save_msg_id(mid):
    with open(MESSAGE_ID_FILE, "w") as f:
        json.dump({"id": mid}, f)


load_data()
load_msg_id()


# ---------------- UTIL ----------------

def get_username(user_id: str):
    """Convierte ID a nombre usando cache del bot"""
    user = bot.get_user(int(user_id))
    if user:
        return user.name
    return f"Usuario"


# ---------------- MENSAJE ----------------

def build_text():
    manana = []
    tarde = []
    noche = []

    for user_id, slots in data.items():
        name = get_username(user_id)

        if "mañana" in slots:
            manana.append(name)
        if "tarde" in slots:
            tarde.append(name)
        if "noche" in slots:
            noche.append(name)

    def fmt(lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    return (
        "🗓️ **HORARIOS DISPONIBILIDAD**\n\n"
        f"🌅 Mañana\n{fmt(manana)}\n\n"
        f"🌇 Tarde\n{fmt(tarde)}\n\n"
        f"🌙 Noche\n{fmt(noche)}"
    )


# ---------------- BOTONES ----------------

class HorariosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def toggle(self, user, slot):
        uid = str(user.id)

        if uid not in data:
            data[uid] = []

        if slot in data[uid]:
            data[uid].remove(slot)
        else:
            data[uid].append(slot)

        save_data()

    async def update_msg(self, interaction):
        await interaction.message.edit(content=build_text(), view=self)

    @discord.ui.button(label="Mañana", style=discord.ButtonStyle.green)
    async def manana(self, interaction, button):
        self.toggle(interaction.user, "mañana")
        await interaction.response.defer()
        await self.update_msg(interaction)

    @discord.ui.button(label="Tarde", style=discord.ButtonStyle.blurple)
    async def tarde(self, interaction, button):
        self.toggle(interaction.user, "tarde")
        await interaction.response.defer()
        await self.update_msg(interaction)

    @discord.ui.button(label="Noche", style=discord.ButtonStyle.gray)
    async def noche(self, interaction, button):
        self.toggle(interaction.user, "noche")
        await interaction.response.defer()
        await self.update_msg(interaction)


# ---------------- BOT ----------------

@bot.event
async def on_ready():
    global MESSAGE_ID

    print(f"Bot conectado como {bot.user}")

    await bot.wait_until_ready()

    # recorrer servidores del bot
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="horarios")

        if channel is None:
            continue

        # si ya existe mensaje guardado
        if MESSAGE_ID is not None:
            try:
                msg = await channel.fetch_message(MESSAGE_ID)
                await msg.edit(content=build_text(), view=HorariosView())
                print("Mensaje actualizado")
                return
            except:
                pass

        # crear mensaje si no existe
        msg = await channel.send(build_text(), view=HorariosView())
        MESSAGE_ID = msg.id
        save_msg_id(MESSAGE_ID)

        print("Mensaje creado automáticamente")
        return
        print("SERVIDORES:")
for g in bot.guilds:
    print(g.name)

bot.run(os.environ["TOKEN"])
