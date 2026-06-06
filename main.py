import os
import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "horarios.json"

data = {
    "mañana": [],
    "tarde": [],
    "noche": []
}

HORARIO_MESSAGE_ID = None


# ---------------- STORAGE ----------------

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load():
    global data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        pass

load()


# ---------------- VIEW (BOTONES) ----------------

class HorarioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def update_user(self, user, slot):
        # quitar de todos
        for k in data:
            if user.name in data[k]:
                data[k].remove(user.name)

        # añadir al nuevo slot
        data[slot].append(user.name)
        save()

    async def refresh_message(self, interaction):
        msg = (
            "🗓️ **HORARIOS DE QUEDADA**\n\n"
            f"🌅 Mañana\n{self.format(data['mañana'])}\n\n"
            f"🌇 Tarde\n{self.format(data['tarde'])}\n\n"
            f"🌙 Noche\n{self.format(data['noche'])}"
        )
        await interaction.message.edit(content=msg, view=self)

    def format(self, lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    @discord.ui.button(label="Mañana", style=discord.ButtonStyle.green)
    async def manana(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_user(interaction.user, "mañana")
        await interaction.response.defer()
        await self.refresh_message(interaction)

    @discord.ui.button(label="Tarde", style=discord.ButtonStyle.blurple)
    async def tarde(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_user(interaction.user, "tarde")
        await interaction.response.defer()
        await self.refresh_message(interaction)

    @discord.ui.button(label="Noche", style=discord.ButtonStyle.gray)
    async def noche(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_user(interaction.user, "noche")
        await interaction.response.defer()
        await self.refresh_message(interaction)


# ---------------- BOT ----------------

def build_text():
    def f(lst):
        return "• " + "\n• ".join(lst) if lst else "• (nadie)"

    return (
        "🗓️ **HORARIOS DE QUEDADA**\n\n"
        f"🌅 Mañana\n{f(data['mañana'])}\n\n"
        f"🌇 Tarde\n{f(data['tarde'])}\n\n"
        f"🌙 Noche\n{f(data['noche'])}"
    )


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def crear_horarios(ctx):
    global HORARIO_MESSAGE_ID

    msg = await ctx.send(build_text(), view=HorarioView())
    HORARIO_MESSAGE_ID = msg.id


@bot.command()
async def horarios(ctx):
    await ctx.send(build_text())


bot.run(os.environ["TOKEN"])
