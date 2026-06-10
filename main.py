import discord
from discord.ext import commands
from discord import app_commands, ui
from flask import Flask
from threading import Thread
import os

# --- إعداد Flask للبقاء نشطاً ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# --- إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# الرومات (ID)
ROOM_CONTROL = 1514153684114739251
ROOM_NEWS = 1514154784846774372
ROOM_URGENT = 1514156912999006238
ROOM_FINAL = 1513927384275882104
ROLE_MENTION = "<@&1478799212312531089>"

# --- Modal للخبر ---
class NewsModal(ui.Modal, title='كتابة خبر'):
    news_content = ui.TextInput(label='اكتب الخبر هنا', style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(ROOM_NEWS)
        await channel.send(f"{ROLE_MENTION}\n\n**خبر جديد:**\n{self.news_content.value}")
        await interaction.response.send_message("تم إرسال الخبر!", ephemeral=True)

# --- واجهة الأزرار ---
class MainView(ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @ui.button(label="خبر", style=discord.ButtonStyle.primary)
    async def btn_news(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(NewsModal())

    @ui.button(label="من ضد من", style=discord.ButtonStyle.secondary)
    async def btn_vs(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("الآن اكتب في الشات: `الرتبة1 ضد الرتبة2 المدة`", ephemeral=True)
        def check(m): return m.channel.id == ROOM_CONTROL and m.author == interaction.user
        msg = await bot.wait_for('message', check=check)
        parts = msg.content.split()
        if len(parts) >= 3:
            channel = bot.get_channel(ROOM_NEWS)
            await channel.send(f"{parts[0]} ضد {parts[1]} | المده: {parts[2]}")

    @ui.button(label="خبر عاجل", style=discord.ButtonStyle.danger)
    async def btn_urgent(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("اكتب الخبر العاجل:", ephemeral=True)
        msg = await bot.wait_for('message', check=lambda m: m.author == interaction.user)
        channel = bot.get_channel(ROOM_URGENT)
        await channel.send(f"{ROLE_MENTION} **خبر عاجل:** {msg.content}")

    @ui.button(label="إرسال نهائي", style=discord.ButtonStyle.success)
    async def btn_final(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("اكتب `الرتبة1 الرتبة2 المدة` للإرسال للروم الأخير", ephemeral=True)
        msg = await bot.wait_for('message', check=lambda m: m.author == interaction.user)
        parts = msg.content.split()
        channel = bot.get_channel(ROOM_FINAL)
        await channel.send(f"{parts[0]} ضد {parts[1]} بعد {parts[2]}")

@bot.command()
async def ابدا(ctx):
    if ctx.channel.id == ROOM_CONTROL:
        await ctx.send("اختر أحد الأوامر:", view=MainView())

bot.run(os.getenv('DISCORD_TOKEN'))
