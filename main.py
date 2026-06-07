import discord
from discord.ext import commands, tasks
from discord import ui
import os, json
from keep_alive import keep_alive

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_USERS = [1306034100544737461, 1383948416975110184]
CODES_FILE = 'codes.json'

# --- نظام الـ Streaming الخفي ---
@tasks.loop(minutes=5)
async def change_status():
    # هذا الرابط هو الذي يجعل زر "Watch" يظهر ويحول المستخدم لرابط تويتش الخاص بك
    stream = discord.Streaming(name="adsqwertt11", url="https://www.twitch.tv/adsqwertt11")
    await bot.change_presence(activity=stream)

@bot.event
async def on_ready():
    change_status.start()
    print(f'✅ السستم يعمل الآن بنجاح مع رابط التويتش!')

# --- الأزرار وقاعدة البيانات ---
def load_codes():
    if not os.path.exists(CODES_FILE): return {"codes": []}
    with open(CODES_FILE, 'r') as f: return json.load(f)

def save_codes(data):
    with open(CODES_FILE, 'w') as f: json.dump(data, f)

class CodeModal(ui.Modal, title='🎫 نظام الأكواد الفوري'):
    code = ui.TextInput(label='أدخل الكود هنا', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        data = load_codes()
        if self.code.value in data['codes']:
            await interaction.response.send_message("🎉 **مبروك! الكود صحيح.**", ephemeral=True)
            data['codes'].remove(self.code.value)
            save_codes(data)
        else:
            await interaction.response.send_message("❌ **كود غير صالح أو تم استخدامه.**", ephemeral=True)

class PersistentView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="تجربة حظك الآن", style=discord.ButtonStyle.blurple, emoji="🔥", custom_id="code_btn")
    async def btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CodeModal())

# --- استقبال الأوامر ---
@bot.event
async def on_message(message):
    if message.author.id not in AUTHORIZED_USERS: return
    
    # إضافة كود (بشكل ذكي)
    if message.channel.id == 1513150814942789784:
        if message.content.lower() in ["نعم", "لا"]: return
        
        await message.channel.send(f"🤖 **سستم:** هل تريد إضافة الكود ` {message.content} ` إلى قاعدة البيانات؟ (نعم/لا)")
        def check(m): return m.author.id == message.author.id and m.content.lower() in ["نعم", "لا"]
        try:
            msg = await bot.wait_for('message', check=check, timeout=30)
            if msg.content.lower() == "نعم":
                data = load_codes()
                data['codes'].append(message.content.strip())
                save_codes(data)
                await message.channel.send("✅ **تمت الإضافة بنجاح.**")
            else:
                await message.channel.send("⚠️ **تم إلغاء الأمر.**")
        except:
            await message.channel.send("⏳ **خطأ: انتهى الوقت أو مدخل غير معروف.**")

    await bot.process_commands(message)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
