import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# إعداد Flask ليبقى البوت نشطاً على Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعدادات البوت
TOKEN = os.environ.get('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قاموس لتخزين الموجات النشطة { "رقم_الموجة": channel_id }
active_waves = {}

# مودال صنع الموجة
class CreateWaveModal(discord.ui.Modal, title='صنع موجة جديدة'):
    wave_id = discord.ui.TextInput(label='رقم الموجة (مثال: 13.7)', placeholder='0.1 - 10009.9', min_length=3, max_length=7)

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        
        # التحقق من الصيغة (بسيطة)
        if w_id in active_waves:
            await interaction.response.send_message("❌ يوجد خطأ: هذه الموجة موجودة بالفعل!", ephemeral=True)
            return

        await interaction.response.send_message(f"جاري صنع الموجه... <a:emoji_1:1514266487479599306>", ephemeral=True)
        
        # إنشاء الروم (مقفل للجميع إلا الشخص)
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(name=f"wave-{w_id}", overwrites=overwrites)
        active_waves[w_id] = channel.id
        
        await interaction.followup.send(f"✅ تم إنشاء الموجه {w_id} بنجاح!", ephemeral=True)

# واجهة الأزرار
class WaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.green)
    async def create_wave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

    @discord.ui.button(label="دخول موجه", style=discord.ButtonStyle.blurple)
    async def join_wave(self, interaction: discord.Interaction, button: discord.ui.Button):
        # هنا يتم إضافة كود البحث والدخول للموجة
        await interaction.response.send_message("جاري الدخول للموجه... (تحتاج لربط البحث)", ephemeral=True)

@bot.command()
async def start_wave(ctx):
    if ctx.message.content == "!887788718":
        await ctx.send("مرحباً بك في نظام Walkie-Talkie:", view=WaveView())

# تشغيل البوت و Flask
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
