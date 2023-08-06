import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv() 

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# リアクション用の絵文字
emoji_dict = {"3": "🎉", "2": "👍", "1": "👀"}

# Botが送信したメッセージのIDを保存するリスト
bot_message_ids = []

@bot.command()
async def create_poll(ctx):
    message = await ctx.send("This is a poll. React with your choice.")
    for emoji in emoji_dict.values():
        await message.add_reaction(emoji)
    # 送信したメッセージのIDをリストに追加
    bot_message_ids.append(message.id)

@bot.event
async def on_raw_reaction_add(payload):
    # リアクションが追加されたメッセージがBotが送信したものでなければ無視
    if payload.message_id not in bot_message_ids:
        return

    if str(payload.emoji) not in emoji_dict.values():
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    for reaction in message.reactions:
        if reaction.emoji != str(payload.emoji):
            await message.remove_reaction(reaction.emoji, payload.member)


bot.run(os.getenv('TOKEN')) # run the bot with the token