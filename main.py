import discord
from discord.ext import commands
from discord import ui
import os

# --- الإعدادات ---
SUPPORT_ROLE_ID = 1474552028545028292
CHANNEL_ID_MSG = 1513150789030510622
CATEGORY_ID = 1513150761654157421
TOKEN = os.environ.get("DISCORD_TOKEN")

# --- نافذة التكت (المودال) ---
class TicketModal(ui.Modal, title="مركز الدعم الفني"):
    reason = ui.TextInput(
        label="ما هو سبب فتح التذكرة؟",
        style=discord.TextStyle.paragraph,
        placeholder="أدخل التفاصيل هنا (شكوى، استفسار، شركة...)",
        required=True,
        min_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        ticket_number = len(category.channels) + 1
        
        # صلاحيات القناة
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            f"ticket-{ticket_number}",
            category=category, overwrites=overwrites
        )
        
        embed = discord.Embed(
            title="🎫 | تذكرة جديدة",
            description=f"**صاحب التذكرة:** {interaction.user.mention}\n**السبب:** {self.reason.value}",
            color=discord.Color.from_rgb(0, 255, 255)
        )
        await channel.send(f"<@{interaction.user.id}> <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls())
        await interaction.response.send_message(f"تم فتح تذكرتك في: {channel.mention}", ephemeral=True)

# --- أزرار التحكم داخل التكت ---
class SupportControls(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=False)
        await interaction.channel.set_permissions(interaction.user, send_messages=True)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"✅ تم استلام التذكرة من قبل: {interaction.user.mention}")

    @ui.button(label="قفل التذكرة", style=discord.ButtonStyle.danger, custom_id="close")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.delete()

# --- زر البدء ---
class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="فتح تذكرة دعم", style=discord.ButtonStyle.green, emoji="🎟")
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
        print(f"البوت يعمل الآن: {self.user}")
        channel = self.get_channel(CHANNEL_ID_MSG)
        embed = discord.Embed(
            title="⚙️ | نظام الدعم الفني",
            description="للحصول على المساعدة، يرجى فتح تذكرة عبر الزر أدناه.",
            color=discord.Color.dark_theme()
        )
        await channel.send(embed=embed, view=TicketLauncher())

bot = MyBot()
bot.run(TOKEN)
