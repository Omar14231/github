import os
import discord
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- إعدادات ---
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

active_waves = {} # { "wave_id": channel_id }

class MainWaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.green, custom_id="btn_create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

    @discord.ui.button(label="دخول موجه", style=discord.ButtonStyle.blurple, custom_id="btn_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(JoinWaveModal())

    @discord.ui.button(label="خروج من الموجه", style=discord.ButtonStyle.red, custom_id="btn_leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LeaveWaveModal())

class CreateWaveModal(discord.ui.Modal, title='صنع موجه'):
    wave_id = discord.ui.TextInput(label='رقم الموجة', placeholder='00.0')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id in active_waves:
            return await interaction.response.send_message("يوجد خطأ ❌: هذه الموجة موجودة بالفعل!", ephemeral=True)
        
        await interaction.response.send_message(f"جاري صنع الموجه... <a:emoji_1:1514266487479599306>", ephemeral=True)
        await asyncio.sleep(5)
        
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        
        # الأذونات: خاص فقط لمن صنعها
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
            interaction.user: discord.PermissionOverwrite(connect=True, view_channel=True)
        }
        
        channel = await guild.create_voice_channel(name=w_id, category=category, overwrites=overwrites)
        active_waves[w_id] = channel.id
        
        await interaction.user.move_to(channel)
        await interaction.followup.send(f"تم العملية ✅", ephemeral=True)

class JoinWaveModal(discord.ui.Modal, title='دخول موجه'):
    wave_id = discord.ui.TextInput(label='رقم الموجة')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id not in active_waves:
            return await interaction.response.send_message("يوجد خطأ ❌: الموجه غير موجودة!", ephemeral=True)
        
        await interaction.response.send_message(f"جاري الدخول للموجه... <a:emoji_1:1514266487479599306>", ephemeral=True)
        await asyncio.sleep(5)
        
        channel = interaction.guild.get_channel(active_waves[w_id])
        await channel.set_permissions(interaction.user, connect=True, view_channel=True)
        await interaction.user.move_to(channel)
        await interaction.followup.send(f"تم العملية ✅", ephemeral=True)

class LeaveWaveModal(discord.ui.Modal, title='خروج من موجه'):
    wave_id = discord.ui.TextInput(label='رقم الموجة التي تريد إخفاءها')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id not in active_waves:
            return await interaction.response.send_message("يوجد خطأ ❌: هذه الموجة غير موجودة!", ephemeral=True)
        
        channel = interaction.guild.get_channel(active_waves[w_id])
        # إخفاء الروم عن المستخدم (سحب الصلاحيات)
        await channel.set_permissions(interaction.user, connect=False, view_channel=False)
        # إخراجه من الصوت
        if interaction.user.voice and interaction.user.voice.channel == channel:
            await interaction.user.move_to(None)
            
        await interaction.response.send_message(f"تم العملية ✅: تم خروجك وإخفاء الموجه {w_id} عنك.", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(MainWaveView())
    print(f'البوت جاهز: {bot.user}')

@bot.command(name="887788718")
async def wave_sys(ctx):
    await ctx.send("📡 **نظام الموجات**\nاختر الإجراء:", view=MainWaveView())

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
