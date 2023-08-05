import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv() 

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def create_poll(ctx):
    message = await ctx.send("This is a poll. React with your choice.")
    for emoji in ["👍", "👀", "🎉"]:
        await message.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) in ["👍", "👀", "🎉"]:
        for react in reaction.message.reactions:
            if str(react) != str(reaction.emoji):
                await reaction.message.remove_reaction(react, user)

bot.run(os.getenv('TOKEN'))