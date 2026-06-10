import os
import discord
import asyncio
import re
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = os.environ.get('DISCORD_TOKEN')
CATEGORY_ID = 1514271813297897645 
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تخزين { "wave_id": {"owner": user_id, "channel": channel_id} }
active_waves = {}

# دالة التأكد من التنسيق (رقم.رقم واحد فقط)
def is_valid_format(w_id):
    # Regex: رقم واحد أو أكثر، ثم نقطة، ثم رقم واحد فقط
    return bool(re.match(r"^\d+\.\d$", w_id))

class MainWaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.green, custom_id="btn_create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

class CreateWaveModal(discord.ui.Modal, title='صنع موجه'):
    wave_id = discord.ui.TextInput(label='رقم الموجة', placeholder='مثال: 19.9')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        
        # 1. التحقق من التنسيق
        if not is_valid_format(w_id):
            return await interaction.response.send_message("❌ خطأ: التنسيق يجب أن يكون (رقم.رقم) مثال: 19.9", ephemeral=True)
        
        # 2. التحقق من عدد الموجات (مسموح موجتين فقط لكل شخص)
        user_waves = [w for w in active_waves.values() if w['owner'] == interaction.user.id]
        if len(user_waves) >= 2:
            return await interaction.response.send_message("❌ لا يمكنك صنع أكثر من موجتين!", ephemeral=True)

        if w_id in active_waves:
            return await interaction.response.send_message("❌ هذه الموجة موجودة بالفعل!", ephemeral=True)

        # 3. الرسالة العامة
        msg = await interaction.channel.send(f"جاري صنع الموجه لـ {interaction.user.mention}... <a:emoji_1:1514266487479599306>")
        await interaction.response.defer(ephemeral=True)
        
        await asyncio.sleep(5)
        
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
            interaction.user: discord.PermissionOverwrite(connect=True, view_channel=True)
        }
        
        channel = await guild.create_voice_channel(name=w_id, category=category, overwrites=overwrites)
        active_waves[w_id] = {"owner": interaction.user.id, "channel": channel.id}
        
        await interaction.user.move_to(channel)
        
        await msg.edit(content=f"تم صنع الموجه {w_id} بنجاح ✅")
        await asyncio.sleep(2)
        await msg.delete()

@bot.event
async def on_ready():
    bot.add_view(MainWaveView())
    print(f'البوت جاهز: {bot.user}')

@bot.command(name="887788718")
async def wave_sys(ctx):
    await ctx.send("📡 **نظام الموجات اللاسلكية**\nاختر الإجراء:", view=MainWaveView())

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
