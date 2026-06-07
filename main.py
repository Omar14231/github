import discord, os, flask, threading
from discord.ext import commands, tasks
from discord import ui

# --- إعداد السيرفر الخفي ---
app = flask.Flask('')
@app.route('/')
def home(): return "SYSTEM IS RUNNING"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# الإعدادات
AUTH = [1306034100544737461, 1383948416975110184]
ROOMS = {
    "codes_in": 1513150814942789784,
    "codes_out": 1513150792998195273,
    "giveaway_in": 1513150816716849252,
    "giveaway_out": 1513150791844757535,
    "news_in": 1513150818583314583,
    "news_out": 1513150800065728513
}

# --- الفخامة (الـ Streaming) ---
@tasks.loop(minutes=2)
async def status_task():
    await bot.change_presence(activity=discord.Streaming(name="adsqwertt11", url="https://www.twitch.tv/adsqwertt11"))

@bot.event
async def on_ready():
    status_task.start()
    print("🚀 [SYSTEM]: النظام جاهز ويعمل بكامل القوة")

# --- منطق الاستقبال الفخم ---
@bot.event
async def on_message(message):
    if message.author.bot or message.author.id not in AUTH: return
    
    # 1. نظام الأخبار
    if message.channel.id == ROOMS["news_in"]:
        await message.channel.send("📢 **[SYSTEM]:** هل تود نشر هذا الخبر للجميع؟ (نعم/لا)")
        try:
            msg = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id and m.content.lower() in ["نعم", "لا"], timeout=30)
            if msg.content.lower() == "نعم":
                out = bot.get_channel(ROOMS["news_out"])
                await out.send(f"<@&1478799212312531089>\n🌟 **خبر عاجل من ماين كرافت:**\n\n{message.content}\n\n━━━━━━━━━━━━━━")
                await message.channel.send("✅ **[SYSTEM]:** تم النشر بنجاح.")
        except: await message.channel.send("❌ **[SYSTEM]:** خطأ أو انتهاء وقت العملية.")

    # 2. نظام الأكواد
    elif message.channel.id == ROOMS["codes_in"]:
        code = message.content.strip()
        if code.lower() in ["نعم", "لا"]: return
        await message.channel.send(f"🤖 **[SYSTEM]:** هل تريد إضافة الكود ` {code} ` للسستم؟ (نعم/لا)")
        try:
            msg = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id and m.content.lower() in ["نعم", "لا"], timeout=30)
            if msg.content.lower() == "نعم":
                with open("codes.txt", "a") as f: f.write(f"{code}\n")
                await message.channel.send("✅ **[SYSTEM]:** تم حفظ الكود في ذاكرة النظام.")
        except: pass

    # 3. نظام الجيف أواي
    elif message.channel.id == ROOMS["giveaway_in"]:
        await message.channel.send("🎁 **[SYSTEM]:** هل تريد بدء الجيف أواي المكتوب؟ (نعم/لا)")
        # يمكن إضافة منطق الجيف أواي هنا بنفس الطريقة
    
    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
