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

# estructura: user_id -> ["mañana","tarde"]
data = {}


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
    try:
        with open(MESSAGE_ID_FILE, "r") as f:
            return json.load(f)["id"]
    except:
        return None


def save_msg_id(mid):
    with open(MESSAGE_ID_FILE, "w") as f:
        json.dump({"id": mid}, f)


load_data()
MESSAGE_ID = load_msg_id()


# ---------------- UI ----------------

def build_text():
    manana = []
    tarde = []
    noche = []

    for user, slots in data.items():
        if "mañana" in slots:
            manana.append(user)
        if "tarde" in slots:
            tarde.append(user)
        if "noche" in slots:
            noche.append(user)

    def fmt(lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    return (
        "🗓️ **HORARIOS DE QUEDADA**\n\n"
        f"🌅 Mañana\n{fmt(manana)}\n\n"
        f"🌇 Tarde\n{fmt(tarde)}\n\n"
        f"🌙 Noche\n{fmt(noche)}"
    )


# ---------------- VIEW ----------------

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

    async def update(self, interaction):
        await interaction.message.edit(content=build_text(), view=self)

    @discord.ui.button(label="Mañana", style=discord.ButtonStyle.green)
    async def manana(self, interaction, button):
        self.toggle(interaction.user, "mañana")
        await interaction.response.defer()
        await self.update(interaction)

    @discord.ui.button(label="Tarde", style=discord.ButtonStyle.blurple)
    async def tarde(self, interaction, button):
        self.toggle(interaction.user, "tarde")
        await interaction.response.defer()
        await self.update(interaction)

    @discord.ui.button(label="Noche", style=discord.ButtonStyle.gray)
    async def noche(self, interaction, button):
        self.toggle(interaction.user, "noche")
        await interaction.response.defer()
        await self.update(interaction)


# ---------------- BOT ----------------

@bot.event
async def on_ready():
    global MESSAGE_ID

    print(f"Bot conectado como {bot.user}")

    # crear mensaje fijo si no existe
    if MESSAGE_ID is None:
        channel = discord.utils.get(bot.get_all_channels(), name="horarios")
        if channel:
            msg = await channel.send(build_text(), view=HorariosView())
            MESSAGE_ID = msg.id
            save_msg_id(MESSAGE_ID)


@bot.command()
async def reset_horarios(ctx):
    global MESSAGE_ID
    msg = await ctx.send(build_text(), view=HorariosView())
    MESSAGE_ID = msg.id
    save_msg_id(MESSAGE_ID)


bot.run(os.environ["TOKEN"])
