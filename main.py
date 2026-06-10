import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# إعداد Flask ليبقى البوت نشطاً
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعدادات البوت
TOKEN = os.environ.get('DISCORD_TOKEN')
CATEGORY_ID = 1514271813297897645  # المجلد المحدد الذي طلبت البوت ينشئ فيه

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

active_waves = {}

class CreateWaveModal(discord.ui.Modal, title='صنع موجة جديدة'):
    wave_id = discord.ui.TextInput(label='رقم الموجة (مثال: 13.7)', placeholder='0.1 - 10009.9', min_length=3, max_length=7)

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        
        if w_id in active_waves:
            await interaction.response.send_message("❌ يوجد خطأ: هذه الموجة موجودة بالفعل!", ephemeral=True)
            return

        await interaction.response.send_message(f"جاري صنع الموجه {w_id} <a:emoji_1:1514266487479599306>", ephemeral=True)
        
        guild = interaction.guild
        # جلب الفئة (Category) المحددة
        category = guild.get_channel(CATEGORY_ID)
        
        # إعداد الأذونات (إخفاء عن الجميع، إظهار لصاحب الموجة فقط)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # إنشاء الروم داخل الفئة المحددة
        channel = await guild.create_text_channel(
            name=f"wave-{w_id}", 
            category=category, 
            overwrites=overwrites
        )
        active_waves[w_id] = channel.id
        
        await interaction.followup.send(f"✅ تم إنشاء الموجه {w_id} بنجاح داخل المجلد المطلوب.", ephemeral=True)

class WaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.green)
    async def create_wave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

    @discord.ui.button(label="دخول موجه", style=discord.ButtonStyle.blurple)
    async def join_wave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("أدخل رقم الموجة للدخول...", ephemeral=True)

@bot.command()
async def wave_sys(ctx):
    if ctx.message.content == "!887788718":
        await ctx.send("نظام الموجات - اختر الإجراء:", view=WaveView())

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
