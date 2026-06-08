import discord
from discord.ext import commands
from discord import ui
import os
from flask import Flask
from threading import Thread

SUPPORT_ROLE_ID = 1474552028545028292
CATEGORY_ID = 1513150761654157421
TWITCH_URL = "https://www.twitch.tv/adsqwertt11"
TOKEN = os.environ.get("DISCORD_TOKEN")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- نظام التذكرة الذكي ---
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
        super().__init__(placeholder="اختر سبب التذكرة...", options=options)

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
        await channel.send(f"{interaction.user.mention} <@&{SUPPORT_ROLE_ID}>", embed=embed, view=SupportControls())
        await interaction.response.edit_message(content=f"✅ تم فتح تذكرتك: {channel.mention}", view=None)

class SupportControls(ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
        self.claimed_by = None # متغير لتخزين من استلم التذكرة

    @ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, custom_id="claim_btn", emoji="✅")
    async def claim(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        
        # حماية: هل تم استلامها من قبل؟
        if self.claimed_by:
            return await interaction.response.send_message(f"⚠️ التذكرة مستلمة بالفعل من قبل {self.claimed_by.mention}", ephemeral=True)
        
        self.claimed_by = interaction.user
        await interaction.channel.set_permissions(interaction.guild.get_role(SUPPORT_ROLE_ID), send_messages=False)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"👤 {interaction.user.mention} يريد استلام التذكرة والبدء بالعمل.")

    @ui.button(label="إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="close_btn", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ للإدارة فقط!", ephemeral=True)
        await interaction.channel.delete()

# --- بقية الكلاسات ---
class SelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketLauncher(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="فتح تذكرة", style=discord.ButtonStyle.green, custom_id="open_btn", emoji="🎟")
    async def open(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("اختر سبب التذكرة:", view=SelectView(), ephemeral=True)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def setup_hook():
    bot.add_view(TicketLauncher())
    bot.add_view(SupportControls())
    bot.add_view(SelectView())

@bot.command()
@commands.has_permissions(administrator=True)
async def يلا(ctx):
    embed = discord.Embed(
        title="✨ | مركز المساعدة الفنية",
        description=f"للطلبات، اضغط الزر أدناه.\n\n💜 **تويتش:** {TWITCH_URL}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=TicketLauncher())
    await ctx.message.delete()

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(TOKEN)
