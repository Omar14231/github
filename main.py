import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# إعداد Flask للحفاظ على البوت نشطاً على Render
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# معرفات الرومات (تم إضافتها كما طلبت)
SAFE_CHANNEL_ID = 1514193632335495208
UNSAFE_CHANNEL_ID = 1514193688774049914

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # تجاهل الرسائل في غير الرومات المحددة
    if message.channel.id not in [SAFE_CHANNEL_ID, UNSAFE_CHANNEL_ID]:
        return

    content = message.content.strip()

    # التحقق من وجود رابط (http/https)
    if not (content.startswith("http://") or content.startswith("https://")):
        await message.channel.send("يرجى إرسال رابط صحيح يبدأ بـ http:// أو https:// للتحقق منه.")
        return

    # المنطق الأمني
    if message.channel.id == SAFE_CHANNEL_ID:
        if content.startswith("https://"):
            await message.channel.send("✅ تم إضافة الرابط: **آمن وموثق.**")
        else:
            await message.channel.send("⚠️ تحذير: هذا الرابط غير آمن (لا يستخدم HTTPS)، تم حذفه من القائمة الآمنة.")
            await message.delete()

    elif message.channel.id == UNSAFE_CHANNEL_ID:
        if content.startswith("http://") and not content.startswith("https://"):
            await message.channel.send("❌ تم إضافة الرابط: **غير آمن (تم رصده في القائمة السوداء).**")
        else:
            await message.channel.send("ℹ️ هذا الرابط يبدو آمنًا، لذا لا ينتمي لقسم الروابط غير الآمنة.")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من المتغيرات البيئية
bot.run(os.environ['DISCORD_TOKEN'])
