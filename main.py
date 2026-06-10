import discord
from discord.ext import commands
from discord.ui import Button, View
import threading
from flask import Flask
import os
TOKEN = os.environ.get('DISCORD_TOKEN')
# إعداد Flask لخدمات الاستضافة مثل Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قاموس لتخزين حالة المستخدمين
# {user_id: {"mode": "news" or "worldcup", "active": True}}
user_sessions = {}

# الرومات المطلوبة
ROOM_TRIGGER = 1514153684114739251
ROOM_NEWS = 1514154784846774372
ROOM_WC = 1514156912999006238

class MenuButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="أخبار", style=discord.ButtonStyle.primary)
    async def news_btn(self, interaction: discord.Interaction, button: Button):
        user_sessions[interaction.user.id] = {"mode": "news", "active": True}
        await interaction.response.send_message("تم تفعيل وضع الأخبار! أي رسالة ستكتبها الآن سيتم إرسالها للروم المخصص.", ephemeral=True)

    @discord.ui.button(label="مونديل", style=discord.ButtonStyle.success)
    async def wc_btn(self, interaction: discord.Interaction, button: Button):
        user_sessions[interaction.user.id] = {"mode": "worldcup", "active": True}
        await interaction.response.send_message("تم تفعيل وضع المونديل! أي رسالة ستكتبها الآن سيتم إرسالها للروم المخصص.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def يلا(ctx):
    if ctx.channel.id == ROOM_TRIGGER:
        await ctx.send("اختر الوضع المناسب:", view=MenuButtons())

@bot.command()
async def الغاء(ctx):
    if ctx.author.id in user_sessions:
        del user_sessions[ctx.author.id]
        await ctx.send("تم الإلغاء بنجاح.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # معالجة الأوامر العادية
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # إذا كان المستخدم في وضع مفعل
    if message.author.id in user_sessions and message.channel.id == ROOM_TRIGGER:
        session = user_sessions[message.author.id]
        
        target_id = ROOM_NEWS if session["mode"] == "news" else ROOM_WC
        channel = bot.get_channel(target_id)
        
        if channel:
            # رسالة بتنسيق فنان (Embed) باللون الأزرق
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.blue()
            )
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
            await channel.send(embed=embed)
            await message.add_reaction("✅") # تأكيد الإرسال

bot.run('TOKEN')

# تشغيل Flask في الخلفية
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
