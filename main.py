import discord
from discord.ext import commands
from discord import ui
import os
from flask import Flask
from threading import Thread

# --- إعدادات النظام ---
SUPPORT_ROLE_ID = 1474552028545028292
CHANNEL_ID_MSG = 1513150789030510622
CATEGORY_ID = 1513150761654157421
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- خادم الحفاظ على البوت (Keep-Alive) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- كلاسات التكت (UI) ---
class TicketModal(ui.Modal, title="『 نظام الدعم الفني 』"):
    reason = ui.TextInput(label="سبب فتح التذكرة؟", style=discord.TextStyle.paragraph, placeholder="اكتب تفاصيل طلبك هنا...", min_length=5, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        ticket_number = len(category.channels) + 1
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category, overwrites=overwrites)
        
        embed = discord.Embed(title="🎟 | تذكرة دعم جديدة", description=f"**المستخدم:** {interaction.user.mention}\n**السبب:** {self.reason.value}", color=discord.Color.blue())
        await channel.send(f"<@{interaction.user.id}> <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls())
        await interaction.response.send_message(f"✅ تم فتح التذكرة بنجاح: {channel.mention}", ephemeral=True)

class SupportControls(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim_support_ticket", emoji="✅")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=False)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"⚠️ تم استلام التذكرة من قبل: {interaction.user.mention}")
    @ui.button(label="إغلاق", style=discord.ButtonStyle.danger, custom_id="close_support_ticket", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.delete()

class TicketLauncher(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_support_ticket", emoji="🎟")
    async def open(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketModal())

# --- تشغيل البوت ---
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(SupportControls())
    async def on_ready(self):
        print(f"تم تسجيل الدخول بنجاح كـ {self.user}")
        channel = self.get_channel(CHANNEL_ID_MSG)
        if channel:
            # مسح الرسائل القديمة (اختياري) لمنع التكرار
            async for message in channel.history(limit=5):
                if message.author == self.user:
                    await message.delete()
            
            embed = discord.Embed(title="⚙️ | مركز المساعدة الفنية", description="أهلاً بك، هل تحتاج لمساعدة؟ اضغط على الزر أدناه لفتح تذكرة.", color=discord.Color.dark_theme())
            await channel.send(embed=embed, view=TicketLauncher())
            print("تم إرسال رسالة التذكرة بنجاح!")

bot = MyBot()

if __name__ == "__main__":
    # تشغيل خادم الويب والبوت معاً
    Thread(target=run).start()
    bot.run(TOKEN)
