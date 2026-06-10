import discord
from discord.ext import commands, tasks
from discord import ui, Embed
import asyncio
import datetime

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# الرومات (أضف الـ IDs الخاصة بك هنا)
ROOM_CONTROL = 1514153684114739251
ROLE_ID = "1478799212312531089"

# دالة تحويل الوقت لثواني
def parse_time(time_str):
    unit = time_str[-1].lower()
    value = int(time_str[:-1])
    if unit == 'm': return value * 60
    if unit == 'h': return value * 3600
    if unit == 'd': return value * 86400
    return value

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def ابدا(ctx):
    if ctx.channel.id == ROOM_CONTROL:
        view = MainView()
        embed = Embed(title="لوحة التحكم الرئيسية", description="اختر الميزة المطلوبة من الأزرار أدناه:", color=0x00aaff)
        await ctx.send(embed=embed, view=view)

class MainView(ui.View):
    def __init__(self): super().__init__(timeout=None)

    @ui.button(label="من ضد من", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def btn_vs(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("اكتب في الشات: `الفريق1 ضد الفريق2 المدة` (مثال: 5m)", ephemeral=True)
        
        def check(m): return m.author == interaction.user and m.channel.id == ROOM_CONTROL
        msg = await bot.wait_for('message', check=check)
        parts = msg.content.split()
        team1, team2, time_raw = parts[0], parts[2], parts[3]
        total_seconds = parse_time(time_raw)

        # إنشاء رسالة العداد
        embed = Embed(title="⚔️ مباراة قادمة", description=f"**{team1}** ضد **{team2}**\n\nالوقت المتبقي: {datetime.timedelta(seconds=total_seconds)}", color=0x00aaff)
        message = await interaction.channel.send(f"<@&{ROLE_ID}>", embed=embed)

        # حلقة تحديث الوقت
        while total_seconds > 0:
            await asyncio.sleep(1 if total_seconds < 3600 else 10)
            total_seconds -= (1 if total_seconds < 3600 else 10)
            embed.description = f"**{team1}** ضد **{team2}**\n\nالوقت المتبقي: {datetime.timedelta(seconds=total_seconds)}"
            await message.edit(embed=embed)
        
        await message.edit(embed=Embed(title="انتهى الوقت!", description=f"المباراة: {team1} vs {team2}", color=0xff0000))

# ضع التوكن الخاص بك هنا أو استخدم os.getenv
bot.run('YOUR_DISCORD_TOKEN')
