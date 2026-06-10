import os
import discord
import asyncio
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

# تخزين { "wave_id": channel_id }
active_waves = {}

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
        if interaction.user.voice and interaction.user.voice.channel and interaction.user.voice.channel.id in active_waves.values():
            await interaction.user.move_to(None)
            await interaction.response.send_message("تم خروجك من الموجة.", ephemeral=True)
        else:
            await interaction.response.send_message("أنت لست داخل موجة حالياً!", ephemeral=True)

class CreateWaveModal(discord.ui.Modal, title='صنع موجة'):
    wave_id = discord.ui.TextInput(label='رقم الموجة', placeholder='مثال: 13.7')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id in active_waves:
            return await interaction.response.send_message("❌ هذه الموجة موجودة بالفعل! استخدم زر الدخول.", ephemeral=True)
        
        await interaction.response.send_message(f"⌛ جاري صنع الموجة {w_id}...", ephemeral=True)
        await asyncio.sleep(5)
        
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        channel = await guild.create_voice_channel(name=w_id, category=category)
        active_waves[w_id] = channel.id
        
        await interaction.user.move_to(channel)
        await interaction.followup.send(f"✅ تم صنع الموجة {w_id} ونقلك إليها.", ephemeral=True)

class JoinWaveModal(discord.ui.Modal, title='دخول موجه'):
    wave_id = discord.ui.TextInput(label='رقم الموجة')

    async def on_submit(self, interaction: discord.Interaction):
        w_id = self.wave_id.value
        if w_id not in active_waves:
            return await interaction.response.send_message("❌ الموجة غير موجودة!", ephemeral=True)
        
        channel = interaction.guild.get_channel(active_waves[w_id])
        await interaction.user.move_to(channel)
        await interaction.response.send_message(f"✅ تم سحبك للموجة {w_id}.", ephemeral=True)

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
