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
WELCOME_CHANNEL_ID = 1514193210329534564

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # إرسال رسالة الترحيب عند التشغيل
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send("🛡️ **مركز الأمن الرقمي متصل وجاهز!**\n\nيرجى إرسال أي رابط هنا (أو في الخاص) وسأقوم بالتحقق منه فوراً للتأكد من أمانه.")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    content = message.content.strip()

    # 1. منطق التحقق من الروابط (يعمل في الرومات المحددة وفي الخاص)
    if message.channel.id in [SAFE_CHANNEL_ID, UNSAFE_CHANNEL_ID] or isinstance(message.channel, discord.DMChannel):
        
        # التحقق من وجود رابط
        if not (content.startswith("http://") or content.startswith("https://")):
            # لا نرد في الخاص على كل كلمة لكي لا نزعج المستخدم، فقط إذا أرسل رابطاً خطأ
            if isinstance(message.channel, discord.DMChannel):
                await message.channel.send("يرجى إرسال رابط صحيح يبدأ بـ http:// أو https:// للتحقق منه.")
            return

        # منطق التصنيف
        if message.channel.id == SAFE_CHANNEL_ID or isinstance(message.channel, discord.DMChannel):
            if content.startswith("https://"):
                await message.channel.send("✅ **آمن:** هذا الرابط يستخدم بروتوكول HTTPS المشفر.")
            else:
                await message.channel.send("⚠️ **تحذير:** هذا الرابط غير آمن (HTTP)، يفضل عدم استخدامه!")
        
        if message.channel.id == UNSAFE_CHANNEL_ID:
            if content.startswith("http://"):
                await message.channel.send("❌ **تم الرصد:** هذا الرابط غير آمن ومصنف كخطر.")
            else:
                await message.channel.send("ℹ️ الرابط يبدو آمنًا، لا ينتمي لقسم المخاطر.")

    await bot.process_commands(message)

# تشغيل البوت باستخدام التوكن من المتغيرات البيئية
bot.run(os.environ['DISCORD_TOKEN'])
