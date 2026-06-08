import discord
from discord.ext import commands

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Streaming(
            name="اسم البث الخاص بك",
            url="https://www.twitch.tv/adsqwertt11"
        )
        await self.bot.change_presence(activity=activity)

async def setup(bot):
    await bot.add_cog(Presence(bot))

