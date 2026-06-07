import discord, os, flask, threading, json
from discord.ext import commands, tasks
from discord import ui

# --- إعداد السيرفر ---
app = flask.Flask('')
@app.route('/')
def home(): return "SYSTEM IS ACTIVE"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

AUTH = [1306034100544737461, 1383948416975110184]
ROOMS = {"in": 1513150814942789784, "out": 1513150792998195273}
DB_FILE = "codes.json"

def load_db():
    if not os.path.exists(DB_FILE): return {"codes": []}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- كلاس الزر (يظهر في الروم الثاني) ---
class CodeModal(ui.Modal, title='🎫 التحقق من الكود'):
    code = ui.TextInput(label='أدخل الكود هنا', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 جاري البحث في السستم...", ephemeral=True)
        import asyncio; await asyncio.sleep(2) # تأخير بسيط للواقعية
        
        db = load_db()
        if self.code.value in db["codes"]:
            db["codes"].remove(self.code.value)
            save_db(db)
            await interaction.edit_original_response(content="✅ **مبروك! الكود صحيح وتم ربحه.**")
        else:
            await interaction.edit_original_response(content="❌ **لا.**")

class MainView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="أدخل كودك", style=discord.ButtonStyle.green, emoji="💎", custom_id="code_btn")
    async def btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CodeModal())

# --- الأحداث ---
@tasks.loop(minutes=2)
async def status_task():
    await bot.change_presence(activity=discord.Streaming(name="adsqwertt11", url="https://www.twitch.tv/adsqwertt11"))

@bot.event
async def on_ready():
    status_task.start()
    # إرسال رسالة الترحيب في الروم الثاني إذا لم تكن موجودة
    channel = bot.get_channel(ROOMS["out"])
    await channel.purge(limit=10) # تنظيف الروم
    await channel.send("💎 **منطقة الأكواد الرسمية**\n\nهنا يتم وضع الأكواد، اضغط الزر بالأسفل لتجربة حظك! ⚡", view=MainView())
    print("🚀 [SYSTEM]: النظام يعمل!")

@bot.event
async def on_message(message):
    if message.author.id not in AUTH or message.channel.id != ROOMS["in"]: return
    
    # إضافة كود بدون إزعاج
    db = load_db()
    db["codes"].append(message.content.strip())
    save_db(db)
    await message.add_reaction("✅") # إشارة صامتة أن الكود انحفظ

bot.run(os.getenv('DISCORD_TOKEN'))
