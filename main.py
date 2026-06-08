import discord
from discord.ext import commands
from discord import app_commands, ui
import os

TOKEN = os.environ.get("DISCORD_TOKEN")
SUPPORT_ROLE_ID = 1474552028545028292
CHANNEL_ID_MSG = 1513150789030510622
CATEGORY_ID = 1513150761654157421

class TicketLauncher(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketModal(ui.Modal, title="سبب فتح التذكرة"):
    reason = ui.Select(placeholder="اختر سبب التذكرة", options=[
        discord.SelectOption(label="اسئلة عامة أو خاصة"),
        discord.SelectOption(label="شكوى"),
        discord.SelectOption(label="شركة"),
        discord.SelectOption(label="اعلان"),
        discord.SelectOption(label="ابي شخص اونر"),
        discord.SelectOption(label="الدعم الفني")
    ])

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        ticket_number = len(category.channels) + 1
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }
        
        channel = await guild.create_text_channel(
            f"✧┇🎟┇✧・تكت・{ticket_number}",
            category=category, overwrites=overwrites
        )
        
        embed = discord.Embed(title="تم فتح التذكرة", description=f"السبب: {self.reason.values[0]}\nيرجى انتظار استلام الدعم الفني.", color=discord.Color.blue())
        await channel.send(f"<@{interaction.user.id}> <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls())
        await interaction.response.send_message(f"تم فتح تذكرتك في {channel.mention}", ephemeral=True)

class SupportControls(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("للإدارة فقط!", ephemeral=True)
        
        button.disabled = True
        await interaction.channel.set_permissions(interaction.user, send_messages=True)
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=False)
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"تم استلام التذكرة من قبل {interaction.user.mention}")

    @ui.button(label="قفل التذكرة", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.channel.delete()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(TicketLauncher())
        self.add_view(SupportControls())

    async def on_ready(self):
        channel = self.get_channel(CHANNEL_ID_MSG)
        embed = discord.Embed(title="الدعم الفني", description="أهلاً بك في الدعم الفني! للأسئلة أو الشكاوي أو أي استفسار، اضغط الزر أدناه.", color=discord.Color.gold())
        await channel.send(embed=embed, view=TicketLauncher())
        print(f"Logged in as {self.user}")

bot = MyBot()
bot.run(TOKEN)
