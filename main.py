import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# المتغيرات الخاصة بك
AUTHORIZED_USERS = [1306034100544737461, 1383948416975110184]
ROOMS = {
    "codes": {"input": 1513150814942789784, "output": 1513150792998195273},
    "giveaway": {"input": 1513150816716849252, "output": 1513150791844757535},
    "news": {"input": 1513150818583314583, "output": 1513150800065728513}
}

@bot.event
async def on_ready():
    print(f'البوت {bot.user} يعمل الآن بنجاح!')

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id not in AUTHORIZED_USERS:
        return

    # نظام أخبار ماين كرافت
    if message.channel.id == ROOMS["news"]["input"]:
        await message.channel.send("هل أنت متأكد من نشر هذا الخبر؟ (نعم/لا)")
        def check(m): return m.author == message.author and m.content.lower() == "نعم"
        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
            target_channel = bot.get_channel(ROOMS["news"]["output"])
            await target_channel.send(f"<@&1478799212312531089>\n**جديد أخبار ماين كرافت:**\n{message.content}")
            await message.channel.send("تم النشر بنجاح!")
        except: pass

    await bot.process_commands(message)

# تشغيل السيرفر للبقاء نشطاً ثم تشغيل البوت
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
