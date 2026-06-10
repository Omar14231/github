import os
import discord
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# إعداد Flask
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعدادات
TOKEN = os.environ.get('DISCORD_TOKEN')
CATEGORY_ID = 1514271813297897645 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تخزين البيانات { "wave_id": {"owner_id": int, "channel_id": int} }
active_waves = {}

class WaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجة", style=discord.ButtonStyle.green, custom_id="create_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateWaveModal())

class CreateWaveModal(discord.ui.Modal, title='صنع موجة جديدة'):
    wave_id = discord.ui.TextInput(label='رقم الموجة', placeholder='مثال: 13.7', min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.wave_id.value
        try:
            num = float(val)
            if not (0.0 <= num <= 100000000000000.0): raise ValueError
        except:
            return await interaction.response.send_message("❌ الرقم غير صحيح! يجب أن يكون بين 0.0 و 100,000,000,000,000.0", ephemeral=True)

        if val in active_waves:
            return await interaction.response.send_message("❌ هذه الموجة موجودة بالفعل!", ephemeral=True)

        await interaction.response.send_message(f"⌛ جاري صنع الموجه {val}...", ephemeral=True)
        await asyncio.sleep(5)
        
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), 
                      interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)}
        
        channel = await guild.create_text_channel(name=str(val), category=category, overwrites=overwrites)
        active_waves[val] = {"owner_id": interaction.user.id, "channel_id": channel.id}
        
        # زر التحكم داخل الروم
        await channel.send(f"✅ تم صنع الموجة {val}!", view=ChannelControlView(val))
        await interaction.followup.send(f"✅ تم صنع الموجه {val} والآن يمكنك الدخول للروم: {channel.mention}")

class ChannelControlView(discord.ui.View):
    def __init__(self, w_id):
        super().__init__(timeout=None)
        self.w_id = w_id

    @discord.ui.button(label="خروج من الموجة", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()
        del active_waves[self.w_id]
        await interaction.response.send_message("تم إغلاق الموجة والخروج منها.")

@bot.event
async def on_ready():
    bot.add_view(WaveView())
    print(f'البوت جاهز: {bot.user}')

@bot.command(name="887788718")
async def wave_sys(ctx):
    await ctx.send("📡 **نظام الموجات اللاسلكية**\nاختر الإجراء المناسب:", view=WaveView())

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)
