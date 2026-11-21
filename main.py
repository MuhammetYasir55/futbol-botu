
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import database

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True
)


@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")
    print("Komutlar kullanima hazir!")

    print("Bagli sunucular:")
    for guild in bot.guilds:
        print("-", guild.name)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print("MESAJ GELDI:", message.content)
    await bot.process_commands(message)


# KAYIT
@bot.command()
async def kayit(ctx):
    result = database.database.register_player(
        ctx.author.id,
        ctx.author.name
    )

    if result:
        await ctx.send("Futbolcu kaydin olusturuldu! +100 puan kazandin.")
    else:
        await ctx.send("Zaten kayitlisin!")


# PROFIL
@bot.command()
async def profil(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    player = database.database.get_player(member.id)

    if player is None:
        await ctx.send("Bu oyuncu kayitli degil!")
        return

    team = database.database.get_team(member.id)
    team_name = team[1] if team else "Takimsiz"

    rating = database.database.get_rating(player[3])

    embed = discord.Embed(
        title=f"{player[1]} - Profil",
        color=discord.Color.blue()
    )

    embed.add_field(name="Oyuncu", value=member.mention)
    embed.add_field(name="Takim", value=team_name)
    embed.add_field(name="Puan", value=player[3])
    embed.add_field(name="Reyting", value=rating)

    await ctx.send(embed=embed)


# PUAN
@bot.command()
async def puan(ctx):
    player = database.database.get_player(ctx.author.id)

    if player is None:
        await ctx.send("Once !kayit yazmalisin.")
        return

    rating = database.database.get_rating(player[3])

    await ctx.send(
        f"**{ctx.author.name}**\n"
        f"Puan: {player[3]}\n"
        f"Reyting: {rating}"
    )


# OYUNCULAR
@bot.command()
async def oyuncular(ctx):
    players = database.database.get_players()

    if not players:
        await ctx.send("Henuz oyuncu yok!")
        return

    message = "**Oyuncular**\n"

    for player in players:
        message += (
            f"{player[0]} - "
            f"{player[2]} puan - "
            f"{database.database.get_rating(player[2])}\n"
        )

    await ctx.send(message)


# TAKIM KUR
@bot.command()
async def takimkur(ctx, *, team_name: str):
    result = database.database.create_team(
        team_name.strip(),
        ctx.author.id
    )

    if result == "not_registered":
        await ctx.send("Once !kayit yaz.")
    elif result == "already_in_team":
        await ctx.send("Zaten bir takimin var!")
    elif result == "team_exists":
        await ctx.send("Bu takim zaten var!")
    elif result == "success":
        await ctx.send(
            f"{team_name} takimi kuruldu! +50 puan kazandin."
        )


# TAKIM BILGISI
@bot.command()
async def takim(ctx):
    team = database.database.get_team(ctx.author.id)

    if team is None:
        await ctx.send("Bir takimin yok!")
        return

    members = database.database.get_team_members(team[0])
    points = database.database.get_team_points(team[0])

    message = (
        f"**Takim: {team[1]}**\n"
        f"Kaptan: <@{team[2]}>\n\n"
    )

    for member in members:
        message += f"{member[0]} - {member[2]} puan\n"

    message += f"\nToplam puan: {points}"

    await ctx.send(message)


# TAKIMA KATIL
@bot.command()
async def takimkatil(ctx, *, team_name: str):
    result = database.database.join_team(
        team_name.strip(),
        ctx.author.id
    )

    if result == "not_registered":
        await ctx.send("Once !kayit yaz.")
    elif result == "already_in_team":
        await ctx.send("Zaten bir takimin var!")
    elif result == "team_not_found":
        await ctx.send("Takim bulunamadi!")
    elif result == "success":
        await ctx.send(f"{team_name} takimina katildin!")


# TAKIMLARI LISTELE
@bot.command()
async def takimlar(ctx):
    db = database.database

    db.cursor.execute("""
        SELECT team_id, team_name
        FROM teams
        ORDER BY team_id
    """)

    teams = db.cursor.fetchall()

    if not teams:
        await ctx.send("Henuz kurulmus takim yok!")
        return

    message = "**Takim Listesi**\n"

    for team in teams:
        message += f"ID: {team[0]} - {team[1]}\n"

    await ctx.send(message)


# MAC SONUCU
@bot.command()
@commands.has_guild_permissions(manage_guild=True)
async def mac(ctx, team1_id: int, team2_id: int, result: str):
    result = result.lower()

    if result not in ("team1", "team2", "draw"):
        await ctx.send(
            "Sonuc team1, team2 veya draw olmali!"
        )
        return

    success = database.database.finish_match(
        team1_id,
        team2_id,
        result
    )

    if not success:
        await ctx.send("Takim ID'lerini kontrol et!")
        return

    if result == "team1":
        await ctx.send(
            f"Mac tamamlandi! {team1_id} numarali takim kazandi. "
            "+30 puan!"
        )
    elif result == "team2":
        await ctx.send(
            f"Mac tamamlandi! {team2_id} numarali takim kazandi. "
            "+30 puan!"
        )
    else:
        await ctx.send(
            "Mac berabere bitti! Iki takimin oyunculari +10 puan kazandi."
        )


# YARDIM
@bot.command()
async def yardim(ctx):
    await ctx.send(
        "**FUTBOL BOTU KOMUTLARI**\n\n"
        "`!kayit` - Kayit ol\n"
        "`!profil` - Profilini goster\n"
        "`!puan` - Puan ve reytingini goster\n"
        "`!oyuncular` - Oyunculari listele\n"
        "`!takimkur TakimAdi` - Takim kur\n"
        "`!takim` - Takimini goster\n"
        "`!takimlar` - Takimlari listele\n"
        "`!takimkatil TakimAdi` - Takima katil\n"
        "`!mac 1 2 team1` - Mac sonucunu kaydet\n"
        "`!yardim` - Yardim"
    )


# HATALAR
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komut icin Sunucuyu Yonet izni gerekiyor!")
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Komut eksik! Kullanimi: !mac 1 2 team1")
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send("Gecersiz bilgi girdin. Takim ID'lerini kontrol et.")
        return

    print("Komut hatasi:", error)
    await ctx.send("Bir hata olustu!")


token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("Token bulunamadi!")
