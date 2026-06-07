import discord
from discord.ext import commands
from discord import ui
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_USERS = [1306034100544737461, 1383948416975110184]
GUILD_ID = 1474476686262145146

# --- كلاسات الأزرار (تفاعلية) ---
class ActionView(ui.View):
    def __init__(self, mode):
        super().__init__(timeout=None)
        self.mode = mode

    @ui.button(label="بدء المشاركة", style=discord.ButtonStyle.green, emoji="🎟️")
    async def join_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EntryModal(self.mode))

class EntryModal(ui.Modal):
    def __init__(self, mode):
        super().__init__(title='نظام السستم')
        self.mode = mode
        self.add_item(ui.TextInput(label='أدخل الكود أو البيانات المطلوبة', style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 جاري فحص البيانات في السستم... يرجى الانتظار.", ephemeral=True)

# --- منطق البوت ---

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print(f'النظام يعمل بكامل كفاءته!')

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id not in AUTHORIZED_USERS: return
    if message.channel.id not in [1513150814942789784, 1513150816716849252, 1513150818583314583]: return

    # 1. نظام أخبار ماين كرافت
    if message.channel.id == 1513150818583314583:
        await message.channel.send("❓ هل أنت متأكد أن هذا هو الخبر الصحيح؟ (نعم/لا)")
        def check(m): return m.author.id == message.author.id and m.content.lower() == "نعم"
        try:
            await bot.wait_for('message', check=check, timeout=30)
            channel = bot.get_channel(1513150800065728513)
            await channel.send(f"<@&1478799212312531089>\n🌟 **أخبار ماين كرافت:**\n\n{message.content}\n\n━━━━━━━━━━━━━━")
            await message.channel.send("✅ تم نشر الخبر بنجاح!")
        except: await message.channel.send("❌ تم إلغاء النشر.")

    # 2. نظام الأكواد
    elif message.channel.id == 1513150814942789784:
        await message.channel.send("❓ هل هذا الكود جاهز للنشر؟ (نعم/لا)")
        if (await bot.wait_for('message', check=lambda m: m.content.lower() == "نعم", timeout=30)):
            channel = bot.get_channel(1513150792998195273)
            await channel.send("💎 **منطقة الأكواد:**\n\nقد تربح جوائز كبيرة أو لا شيء في بعض الأحيان.\nاضغط الزر أدناه لتجربة حظك! 👇", view=ActionView("code"))

    # 3. نظام الجيف أواي
    elif message.channel.id == 1513150816716849252:
        await message.channel.send("❓ هل هذا هو اسم الجيف أواي والمده؟ (نعم/لا)")
        if (await bot.wait_for('message', check=lambda m: m.content.lower() == "نعم", timeout=30)):
            channel = bot.get_channel(1513150791844757535)
            await channel.send("🎁 **جيف أواي جديد!**\n\nاضغط الزر أدناه لتشارك في الفرصة!", view=ActionView("giveaway"))

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
