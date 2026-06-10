import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# إعداد Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعدادات البوت
TOKEN = os.environ.get('DISCORD_TOKEN')
CATEGORY_ID = 1514271813297897645 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قاموس لتخزين الموجات
active_waves = {}

# --- النماذج والأزرار ---
class CreateWaveModal(discord.ui.Modal, title='صنع موجة'):
    wave_id = discord.ui.TextInput(label='رقم الموجة (مثال: 13.7)', min_length=3, max_length=7)

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id in active_waves:
            await interaction.response.send_message("❌ خطأ: الموجة موجودة بالفعل!", ephemeral=True)
            return

        await interaction.response.send_message(f"جاري صنع الموجه {w_id} <a:emoji_1:1514266487479599306>", ephemeral=True)
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        channel = await guild.create_text_channel(name=f"wave-{w_id}", category=category, overwrites=overwrites)
        active_waves[w_id] = channel.id
        await interaction.followup.send(f"✅ تم صنع الموجه {w_id}", ephemeral=True)

class WaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.green, custom_id="create_wave_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

    @discord.ui.button(label="دخول موجه", style=discord.ButtonStyle.blurple, custom_id="join_wave_btn")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("ميزة الدخول تحت التطوير.", ephemeral=True)

# --- تشغيل البوت ---
@bot.event
async def on_ready():
    bot.add_view(WaveView()) # هذا السطر يضمن بقاء الأزرار فعالة دائماً
    print(f'البوت يعمل: {bot.user}')

@bot.command(name="887788718")
async def wave_sys(ctx):
    await ctx.send("نظام الموجات - اختر الإجراء:", view=WaveView())

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
