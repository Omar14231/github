import discord, os, flask, threading, json, asyncio
from discord.ext import commands, tasks
from discord import ui

# --- إعداد السيرفر الخفي ---
app = flask.Flask('')
@app.route('/')
def home(): return "SYSTEM IS ONLINE"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# الإعدادات
AUTH = [1306034100544737461, 1383948416975110184]
ROOMS = {
    "codes_in": 1513150814942789784, "codes_out": 1513150792998195273, "codes_logs": 1513210251984502784,
    "give_in": 1513150816716849252, "give_out": 1513150791844757535,
    "news_in": 1513150818583314583, "news_out": 1513150800065728513
}

def load_db():
    if not os.path.exists("codes.json"): return {"codes": {}}
    with open("codes.json", "r") as f: return json.load(f)

def save_db(data):
    with open("codes.json", "w") as f: json.dump(data, f)

# --- كلاس الأزرار ---
class CodeView(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="تجربة حظك", style=discord.ButtonStyle.blurple, custom_id="code_btn")
    async def btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CodeModal())

class CodeModal(ui.Modal, title='🎫 التحقق من الكود'):
    code = ui.TextInput(label='أدخل الكود:', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 جاري البحث في السستم...", ephemeral=True)
        await asyncio.sleep(2)
        db = load_db()
        if self.code.value in db["codes"]:
            prize = db["codes"].pop(self.code.value)
            save_db(db)
            await interaction.edit_original_response(content=f"🎉 مبروك! ربحت: {prize}")
            log = bot.get_channel(ROOMS["codes_logs"])
            await log.send(f"🏆 **فائز جديد!**\n👤 الشخص: {interaction.user.mention}\n💎 الجائزة: {prize}\n🎟️ الكود: `{self.code.value}`")
        else:
            await interaction.edit_original_response(content="❌ لا.")

# --- منطق البوت ---
@tasks.loop(minutes=2)
async def status_task():
    await bot.change_presence(activity=discord.Streaming(name="adsqwertt11", url="https://www.twitch.tv/adsqwertt11"))

@bot.event
async def on_ready():
    status_task.start()
    print("🚀 [SYSTEM]: النظام يعمل!")

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id not in AUTH: return
    
    # 1. نظام الأكواد
    if message.channel.id == ROOMS["codes_in"]:
        code = message.content.strip()
        await message.channel.send("❓ هل أنت متأكد من إضافة هذا الكود؟ (نعم/لا)")
        try:
            msg = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id, timeout=30)
            if msg.content.lower() == "نعم":
                await message.channel.send("🎁 ما هي الهدية؟")
                prize_msg = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id, timeout=30)
                db = load_db()
                db["codes"][code] = prize_msg.content
                save_db(db)
                await message.channel.send("✅ تم الإضافة بنجاح!")
            else: await message.channel.send("❌ تم الإلغاء.")
        except: await message.channel.send("❌ غير مفهوم، تم الإلغاء.")

    # 2. نظام الجيف أواي
    elif message.channel.id == ROOMS["give_in"]:
        await message.channel.send("❓ هل هذا اسم الجيف أواي؟ (نعم/لا)")
        try:
            m = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id, timeout=30)
            if m.content.lower() == "نعم":
                await message.channel.send("⏱️ حدد المدة (مثال: 10h, 5m):")
                time = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id, timeout=30)
                out = bot.get_channel(ROOMS["give_out"])
                await out.send(f"🎁 **جيف أواي: {message.content}**\n⏳ المدة: {time.content}\n✨ اضغط الزر للمشاركة!")
                await message.channel.send("✅ تم النشر.")
        except: await message.channel.send("❌ تم الإلغاء.")

    # 3. نظام الأخبار
    elif message.channel.id == ROOMS["news_in"]:
        await message.channel.send("❓ متأكد من النشر؟ (نعم/لا)")
        try:
            m = await bot.wait_for('message', check=lambda m: m.author.id == message.author.id, timeout=30)
            if m.content.lower() == "نعم":
                out = bot.get_channel(ROOMS["news_out"])
                await out.send(f"<@&1478799212312531089>\n📢 **خبر جديد:**\n{message.content}")
                await message.channel.send("✅ تم النشر.")
        except: await message.channel.send("❌ تم الإلغاء.")

bot.run(os.getenv('DISCORD_TOKEN'))
