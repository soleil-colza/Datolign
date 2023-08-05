# discord.pyのインポート

from codeop import CommandCompiler
import pip
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.reactions = True  # リアクションを有効にする！

bot = CommandCompiler.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
# メンションされるとon_messageイベントがトリガーされる
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
       
        # 要置き換え、両変数に仮の値を代入してます
        deadline = '8/10 0:00'
        participants = ['User1', 'User2', 'User3'] #リスト'participants'にサーバー内のbot以外のユーザーを入れる

        # 提案する日程を生成
        suggested_dates = generate_suggested_dates(deadline)

        # 日程を提案するメッセージをbot側から送信
        response = f"**Deadline**: {deadline}\n\n**Suggested Dates**:\n"
        for date in suggested_dates:
            response += f"{date}\n"

        await message.channel.send(response)

def generate_suggested_dates(deadline):
    # Replace this with your logic to generate the suggested dates based on participants' availability and the deadline

    return [] # 日程をリストで返す

# **'_BOT_TOKEN'は後ほど実際のトークンで置き換えが必要**
bot.run('BOT_TOKEN')

