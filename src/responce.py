import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# リアクションの集計用の辞書を初期化
reaction_count = {}
candidate_dates = []


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Botが送信したメッセージには反応しない
        return

    await bot.process_commands(message)


@bot.event
async def on_reaction(reaction, user):
    if user == bot.user:
        # Bot自身のリアクションには反応しない
        return
    channel = reaction.message.channel
    members = channel.guild.members
    # ボットを考慮しない人数
    member_count = sum(not member.bot for member in members)
    message_id = reaction.message.id
    message = await channel.fetch_message(message_id)
    content = message.content
    emoji = str(reaction.emoji)

    if content not in reaction_count:
        reaction_count[content] = {}

    # メッセージの集計
    reaction_count[content][emoji] = reaction_count[content].get(emoji, 0) + 1
    max_score = -1
    result = []
    for message in reaction_count.keys():
        reactions = reaction_count[message]
        if sum(reactions.values()) == member_count + 1:
            point_3 = reactions.get("🎉", 0)
            point_2 = reactions.get("👀", 0)
            point_1 = reactions.get("👍", 0)
            score = point_3 * 3 + point_2 * 2 + point_1
            if max_score < score:
                max_score = score
                result = [[score, message]]
            elif max_score == score:
                result.append([score, message])
    if len(result) > 1:
        times = [time[1] for time in result]
        await channel.send(f"最大票の日程が{len(result)}件あります\n{''.join(str(x) for x in times)}")
    elif len(result) == 1:
        await channel.send(f"最大票の日程\n{result[0][1]}")


@bot.command()
async def sendMessage(ctx):
    # メッセージを送信
    sent_message = await ctx.send("これはテストメッセージです。リアクションをつけてください！")


# bot.run(TOKEN)