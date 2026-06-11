import discord
import asyncio
import os
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')
CATEGORY_ID = 1514271813297897645 

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

active_waves = {} 

class WaveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="صنع موجه", style=discord.ButtonStyle.primary, custom_id="btn_create")
    async def create(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_modal(CreateModal())

    @discord.ui.button(label="دخول موجه", style=discord.ButtonStyle.primary, custom_id="btn_join")
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_modal(JoinModal())

    @discord.ui.button(label="خروج من الموجه", style=discord.ButtonStyle.primary, custom_id="btn_leave")
    async def leave(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_modal(LeaveModal())

class CreateModal(discord.ui.Modal, title='صنع موجه'):
    w_id = discord.ui.TextInput(label='رقم الموجة (مثال: 19.9)')
    
    async def on_submit(self, i: discord.Interaction):
        w_id = self.w_id.value
        # التحقق من أن رقم الموجه لا يتكرر
        if w_id in active_waves:
            return await i.response.send_message("❌ خطأ: هذه الموجة موجودة بالفعل!", ephemeral=True)
        
        # حجز الرقم فوراً لمنع التكرار
        active_waves[w_id] = "pending" 
        
        guild = i.guild
        category = guild.get_channel(CATEGORY_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            i.user: discord.PermissionOverwrite(view_channel=True, connect=True)
        }
        
        channel = await guild.create_voice_channel(name=w_id, category=category, overwrites=overwrites)
        active_waves[w_id] = {"owner": i.user.id, "channel": channel.id}
        
        await i.user.move_to(channel)
        
        msg = await i.channel.send("تم صنع الموجه بنجاح ✅")
        await asyncio.sleep(3)
        await msg.delete()

class JoinModal(discord.ui.Modal, title='دخول موجه'):
    w_id = discord.ui.TextInput(label='رقم الموجة')
    
    async def on_submit(self, i: discord.Interaction):
        w_id = self.w_id.value
        if w_id not in active_waves or active_waves[w_id] == "pending":
            return await i.response.send_message("❌ خطأ: الموجه غير موجودة!", ephemeral=True)
        
        ch = i.guild.get_channel(active_waves[w_id]['channel'])
        await ch.set_permissions(i.user, view_channel=True, connect=True)
        await i.user.move_to(ch)
        await i.response.send_message("تم الدخول بنجاح ✅", ephemeral=True)

class LeaveModal(discord.ui.Modal, title='خروج من موجه'):
    w_id = discord.ui.TextInput(label='رقم الموجة')
    
    async def on_submit(self, i: discord.Interaction):
        w_id = self.w_id.value
        if w_id not in active_waves:
            return await i.response.send_message("❌ خطأ: الموجه غير موجودة!", ephemeral=True)
        
        ch = i.guild.get_channel(active_waves[w_id]['channel'])
        await ch.set_permissions(i.user, view_channel=False, connect=False)
        if i.user.voice and i.user.voice.channel == ch:
            await i.user.move_to(None)
        await i.response.send_message("تم الخروج وإخفاء الموجه ✅", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(WaveView())
    print(f'البوت {bot.user} جاهز للعمل!')

@bot.command(name="887788718")
async def setup(ctx): 
    await ctx.send("📡 **نظام الموجات اللاسلكية**\nاختر الإجراء:", view=WaveView())

bot.run(TOKEN)
