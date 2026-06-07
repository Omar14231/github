import discord
from discord.ext import commands
from discord import ui
import os
from keep_alive import keep_alive

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_USERS = [1306034100544737461, 1383948416975110184]
GUILD_ID = 1474476686262145146

# --- كلاسات الأزرار (Buttons & Modals) ---

class CodeModal(ui.Modal, title='نظام التحقق'):
    code = ui.TextInput(label='اكتب الكود الخاص بك', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 جاري البحث عن الكود في السستم...", ephemeral=True)

class GiveawayModal(ui.Modal, title='المشاركة في الجيف أواي'):
    name = ui.TextInput(label='اكتب اسمك للمشاركة', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ تم تسجيلك بنجاح في الجيف أواي!", ephemeral=True)

class ActionView(ui.View):
    def __init__(self, mode):
        super().__init__(timeout=None)
        self.mode = mode
    
    @ui.button(label="اضغط للمشاركة", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: ui.Button):
        if self.mode == "code":
            await interaction.response.send_modal(CodeModal())
        else:
            await interaction.response.send_modal(GiveawayModal())

# --- الأحداث الأساسية ---

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.invisible)
    print(f'النظام يعمل الآن في وضع التخفي')

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None or message.guild.id != GUILD_ID:
        return
    if message.author.id not in AUTHORIZED_USERS:
        return

    # 1. أخبار ماين كرافت
    if message.channel.id == 1513150818583314583:
        channel = bot.get_channel(1513150800065728513)
        await channel.send(f"<@&1478799212312531089>\n📢 **خبر جديد:**\n{message.content}")

    # 2. الأكواد
    elif message.channel.id == 1513150814942789784:
        channel = bot.get_channel(1513150792998195273)
        await channel.send("⚠️ **تنبيه:** هذه المنطقة قد تربح منها جوائز كبيرة أو لا شيء. اكتب الكود للبدء:", view=ActionView("code"))

    # 3. الجيف أواي
    elif message.channel.id == 1513150816716849252:
        channel = bot.get_channel(1513150791844757535)
        await channel.send("🎁 **جيف أواي جديد!** اضغط الزر للمشاركة:", view=ActionView("giveaway"))

    await bot.process_commands(message)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
