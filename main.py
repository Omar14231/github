import discord
from discord.ext import commands
from discord import ui
import os
from flask import Flask
from threading import Thread

# --- الإعدادات ---
SUPPORT_ROLE_ID = 1513675420774699168
CATEGORY_ID = 1513671321521885215
TWITCH_URL = "https://discord.com/channels/1513668407608868967/1513669950475210963"
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- خادم الحفاظ على البوت ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- القائمة المنسدلة لاختيار اللغة ---
class TicketSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="English", emoji="🇺🇸", value="en"),
            discord.SelectOption(label="العربية", emoji="🇸🇦", value="ar")
        ]
        super().__init__(placeholder="اختر لغة التذكرة / Choose ticket language...", options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        ticket_number = len(category.channels) + 1
        lang = self.values[0]
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category, overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎟 | تذكرة دعم جديدة" if lang == "ar" else "🎟 | New Support Ticket", 
            description=f"**صاحب التذكرة / Ticket Owner:** {interaction.user.mention}\n**الغه / Language:** {lang}", 
            color=discord.Color.blue()
        )
        await channel.send(f"{interaction.user.mention} <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls(lang=lang))
        response_text = f"✅ تم فتح تذكرتك في: {channel.mention}" if lang == "ar" else f"✅ Your ticket has been opened in: {channel.mention}"
        await interaction.response.edit_message(content=response_text, view=None)

class SelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- أزرار التحكم (استلام/قفل) ---
class SupportControls(ui.View):
    def __init__(self, lang="ar"): 
        super().__init__(timeout=None)
        self.lang = lang
        if lang == "en":
            self.claim_btn.label = "Claim Ticket"
            self.close_btn.label = "Close Ticket"
        else:
            self.claim_btn.label = "استلام التذكرة"
            self.close_btn.label = "إغلاق التذكرة"

    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim_btn", emoji="✅")
    async def claim_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            err_msg = "❌ هذه الأزرار للإدارة فقط!" if self.lang == "ar" else "❌ These buttons are for staff only!"
            return await interaction.response.send_message(err_msg, ephemeral=True)
        
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=True) # تم التعديل للسماح
        button.disabled = True
        await interaction.response.edit_message(view=self)
        msg = f"⚠️ تم استلام التذكرة من قبل: {interaction.user.mention}" if self.lang == "ar" else f"⚠️ Ticket claimed by: {interaction.user.mention}"
        await interaction.channel.send(msg)

    @ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="close_btn", emoji="🔒")
    async def close_btn(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            err_msg = "❌ هذه الأزرار للإدارة فقط!" if self.lang == "ar" else "❌ These buttons are for staff only!"
            return await interaction.response.send_message(err_msg, ephemeral=True)
        await interaction.channel.delete()

# --- زر فتح التذكرة ---
class TicketLauncher(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="فتح تذكرة / Open Ticket", style=discord.ButtonStyle.green, custom_id="open_btn", emoji="🎟")
    async def open(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("الرجاء اختيار اللغة / Please select language:", view=SelectView(), ephemeral=True)

# --- البوت ---
class MyBot(commands.Bot):
    def __init__(self): super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(SupportControls())
        self.add_view(SelectView())
        
    async def on_ready(self):
        print(f"البوت يعمل الآن كـ {self.user}")

bot = MyBot()

@bot.command()
@commands.has_permissions(administrator=True)
async def يلا(ctx):
    embed = discord.Embed(
        title="✨ | مركز المساعدة الفنية / Support Center",
        description=f"أهلاً بك، هل تحتاج لمساعدة؟ اضغط على الزر أدناه.\nWelcome, do you need help? Click the button below.\n\n━━━━━━━━━━━━━━\n💜 **𝐑𝐞𝐚𝐝 𝐭𝐡𝐞 𝐫𝐮𝐥𝐞𝐬:**\n{TWITCH_URL}\n━━━━━━━━━━━━━━",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=TicketLauncher())
    await ctx.message.delete()

if __name__ == "__main__":
    Thread(target=run).start() 
    bot.run(TOKEN)
