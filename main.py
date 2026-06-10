import discord
import asyncio
import re
from discord.ext import commands

# الإعدادات
TOKEN = 'ضع_التوكن_هنا'
CATEGORY_ID = 1514271813297897645 

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تخزين: { "wave_id": {"owner": user_id, "channel": channel_id} }
active_waves = {}

def is_valid(w_id): return bool(re.match(r"^\d+\.\d$", w_id))

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
        if not is_valid(w_id): return await i.response.send_message("❌ التنسيق يجب أن يكون (رقم.رقم)", ephemeral=True)
        if any(w['owner'] == i.user.id for w in active_waves.values()): return await i.response.send_message("❌ لديك موجه بالفعل!", ephemeral=True)
        if w_id in active_waves: return await i.response.send_message("❌ الموجة موجودة!", ephemeral=True)
        
        msg = await i.channel.send(f"جاري صنع الموجه {w_id} لـ {i.user.mention}... <a:emoji_1:1514266487479599306>")
        await i.response.defer(ephemeral=True)
        await asyncio.sleep(5)
        
        overwrites = {i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True, connect=True)}
        ch = await i.guild.create_voice_channel(name=w_id, category=i.guild.get_channel(CATEGORY_ID), overwrites=overwrites)
        active_waves[w_id] = {"owner": i.user.id, "channel": ch.id}
        await i.user.move_to(ch)
        await msg.edit(content=f"تم صنع الموجه {w_id} بنجاح ✅")
        await asyncio.sleep(2)
        await msg.delete()

class JoinModal(discord.ui.Modal, title='دخول موجه'):
    w_id = discord.ui.TextInput(label='رقم الموجة')
    async def on_submit(self, i: discord.Interaction):
        w_id = self.w_id.value
        if w_id not in active_waves: return await i.response.send_message("❌ الموجه غير موجودة!", ephemeral=True)
        msg = await i.channel.send(f"جاري الدخول للموجه {w_id} لـ {i.user.mention}... <a:emoji_1:1514266487479599306>")
        await i.response.defer(ephemeral=True)
        await asyncio.sleep(5)
        ch = i.guild.get_channel(active_waves[w_id]['channel'])
        await ch.set_permissions(i.user, view_channel=True, connect=True)
        await i.user.move_to(ch)
        await msg.edit(content=f"تم الدخول بنجاح ✅")
        await asyncio.sleep(2)
        await msg.delete()

class LeaveModal(discord.ui.Modal, title='خروج من موجه'):
    w_id = discord.ui.TextInput(label='رقم الموجة')
    async def on_submit(self, i: discord.Interaction):
        w_id = self.w_id.value
        if w_id not in active_waves: return await i.response.send_message("❌ الموجة غير موجودة!", ephemeral=True)
        ch = i.guild.get_channel(active_waves[w_id]['channel'])
        await ch.set_permissions(i.user, view_channel=False, connect=False)
        if i.user.voice and i.user.voice.channel == ch: await i.user.move_to(None)
        await i.response.send_message(f"تم الخروج النهائي من الموجه {w_id} ✅", ephemeral=True)

@bot.command(name="887788718")
async def setup(ctx): await ctx.send("📡 **نظام الموجات اللاسلكية**\nاختر الإجراء:", view=WaveView())

bot.run(TOKEN)
