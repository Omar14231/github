import discord
from discord.ext import commands
from discord import ui
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
SUPPORT_ROLE_ID = 1474552028545028292
CHANNEL_ID_MSG = 1513150789030510622
CATEGORY_ID = 1513150761654157421
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- خادم الحفاظ على البوت ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- القائمة المنسدلة (اختيار السبب) ---
class TicketSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="اسئلة عامة", emoji="❓", value="اسئلة عامة"),
            discord.SelectOption(label="شكوى", emoji="⚠️", value="شكوى"),
            discord.SelectOption(label="طلب شركة", emoji="🏢", value="شركة"),
            discord.SelectOption(label="إعلان", emoji="📢", value="إعلان"),
            discord.SelectOption(label="طلب أونر", emoji="👑", value="طلب أونر"),
            discord.SelectOption(label="دعم فني", emoji="🛠️", value="دعم فني")
        ]
        super().__init__(placeholder="اختر سبب التذكرة من هنا...", options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        ticket_number = len(category.channels) + 1
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category, overwrites=overwrites)
        
        embed = discord.Embed(title="🎟 | تذكرة جديدة", description=f"**المستخدم:** {interaction.user.mention}\n**السبب:** {self.values[0]}", color=discord.Color.blue())
        await channel.send(f"<@{interaction.user.id}> <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls())
        await interaction.response.edit_message(content=f"✅ تم فتح تذكرتك: {channel.mention}", view=None)

class SelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- أزرار التحكم ---
class SupportControls(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim_btn", emoji="✅")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ هذه الأزرار للإدارة فقط!", ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=False)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"⚠️ تم استلام التذكرة من قبل: {interaction.user.mention}")

    @ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="close_btn", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ هذه الأزرار للإدارة فقط!", ephemeral=True)
        await interaction.channel.delete()

# --- الزر الرئيسي ---
class TicketLauncher(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_btn", emoji="🎟")
    async def open(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("اختر سبب التذكرة:", view=SelectView(), ephemeral=True)

# --- تشغيل البوت ---
class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(SupportControls())
        self.add_view(SelectView())
    async def on_ready(self):
        print(f"البوت يعمل: {self.user}")

bot = MyBot()
if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(TOKEN)
