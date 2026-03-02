import discord
import random
from discord.ext import commands

# ===== INTENTS =====
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== CONFIGURAÇÕES =====

# Cargo automático ao entrar
CARGO_AUTO = 1477819943721500813

# ===== TICKETS =====
CATEGORIA_TICKETS = 1477825557789151363
CARGO_STAFF = 1477819276483362816

tickets_abertos = set()

# ===== CARGOS INTERATIVOS =====
CARGO_REMOVER = 1477819943721500813
CARGO_GANHAR = 1477818927584121055

REACTION_ROLES = {
    "🎮": 1478012828148564059,
    "📱": 1478012903176278097,
    "🎬": 1478013038702497867
}

# ===== SENSI =====
sensi_geradas = set()

# ===== EVENTOS =====
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")

@bot.event
async def on_member_join(member):
    cargo = member.guild.get_role(CARGO_AUTO)
    if cargo:
        await member.add_roles(cargo)

# ===== CARGOS POR REAÇÃO =====
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    emoji = str(payload.emoji)
    if emoji not in REACTION_ROLES:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if not member:
        return

    cargo_interativo = guild.get_role(REACTION_ROLES[emoji])
    cargo_remover = guild.get_role(CARGO_REMOVER)
    cargo_ganhar = guild.get_role(CARGO_GANHAR)

    if cargo_interativo:
        await member.add_roles(cargo_interativo)

    if cargo_remover and cargo_remover in member.roles:
        await member.remove_roles(cargo_remover)

    if cargo_ganhar:
        await member.add_roles(cargo_ganhar)

# ===== BOTÃO FECHAR TICKET =====
class FecharTicket(discord.ui.View):
    def __init__(self, dono_id):
        super().__init__(timeout=None)
        self.dono_id = dono_id

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.danger)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.dono_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas o dono do ticket ou a staff pode fechar.",
                ephemeral=True
            )
            return

        tickets_abertos.discard(self.dono_id)
        await interaction.channel.delete()

# ===== SELECT MENU TICKET =====
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Denúncia", emoji="📢"),
            discord.SelectOption(label="Atendimento", emoji="🛠️")
        ]
        super().__init__(
            placeholder="Selecione uma opção",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if user.id in tickets_abertos:
            await interaction.response.send_message(
                "❌ Você já possui um ticket aberto.",
                ephemeral=True
            )
            return

        categoria = guild.get_channel(CATEGORIA_TICKETS)
        staff = guild.get_role(CARGO_STAFF)

        canal = await guild.create_text_channel(
            f"ticket-{user.name}",
            category=categoria,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True),
                staff: discord.PermissionOverwrite(view_channel=True)
            }
        )

        tickets_abertos.add(user.id)

        embed = discord.Embed(
            title="🎟️ Ticket Aberto",
            description=f"{user.mention}, explique sua situação.",
            color=discord.Color.green()
        )

        await canal.send(embed=embed, view=FecharTicket(user.id))
        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}",
            ephemeral=True
        )

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# ===== GERADOR DE SENSI =====
class GerarNovamenteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="🔁 Gerar novamente", style=discord.ButtonStyle.secondary)
    async def gerar(self, interaction: discord.Interaction, button: discord.ui.Button):
        sensi_geradas.discard(interaction.user.id)
        await interaction.response.send_message(
            "♻️ Você pode gerar novamente.",
            ephemeral=True
        )

class SensiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def gerar(self, interaction: discord.Interaction):
        user = interaction.user

        if user.id in sensi_geradas:
            await interaction.response.send_message(
                "❌ Você já gerou sua sensi.",
                view=GerarNovamenteView(),
                ephemeral=True
            )
            return

        geral = random.randint(188, 200)
        ponto = random.randint(192, 200)

        mensagem = (
            "🎯 SUA SENSIBILIDADE\n\n"
            f"Geral: {geral}\n"
            f"Ponto Vermelho: {ponto}\n"
            "Miras: 200\n"
            "Botão: 0\n\n"
            "🔥 Boa pra subir capa!"
        )

        try:
            await user.send(mensagem)
            sensi_geradas.add(user.id)
            await interaction.response.send_message(
                "✅ Sensi enviada no seu privado!",
                ephemeral=True
            )
        except:
            await interaction.response.send_message(
                "❌ Ative sua DM para receber a sensi.",
                ephemeral=True
            )

    @discord.ui.button(label="📱 IOS", style=discord.ButtonStyle.primary)
    async def ios(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerar(interaction)

    @discord.ui.button(label="🤖 Android", style=discord.ButtonStyle.success)
    async def android(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gerar(interaction)

# ===== COMANDOS =====
@bot.command()
@commands.has_permissions(administrator=True)
async def cargos(ctx):
    embed = discord.Embed(
        title="🎭 Cargos Interativos",
        description=(
            "Reaja para receber um cargo:\n\n"
            "🎮 **171**\n"
            "📱 **Full Capa**\n"
            "🎬 **Muita Movi**\n\n"
            "Ao reagir:\n"
            "• Você perde o cargo padrão\n"
            "• Ganha o novo cargo automaticamente"
        ),
        color=discord.Color.green()
    )

    msg = await ctx.send(embed=embed)

    for emoji in REACTION_ROLES:
        await msg.add_reaction(emoji)
        
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description="Abra um ticket usando o menu abaixo.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def sensi(ctx):
    embed = discord.Embed(
        title="🎯 Gerador de Sensibilidade",
        description="Escolha IOS ou Android.\nApenas 1 geração por pessoa.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, view=SensiView())

@bot.command()
async def ping(ctx):
    await ctx.send("pong 🏓")

# ===== TOKEN =====
bot.run("token")
