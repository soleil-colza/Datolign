import discord
from discord.ext import commands
import asyncio
import calendar
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


async def show_calendar(ctx):
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    selected_date = now.day  # 選択中の日付け

    # カレンダーの形式のメッセージを作成
    calendar_message, emoji = _create_calendar_message(current_month, current_year, selected_date)

    # カレンダーをメッセージとして送信
    message = await ctx.send(calendar_message)

    # 月の変更，日付けの変更用のリアクションを付与
    await message.add_reaction("⏪")
    await message.add_reaction("◀")
    await message.add_reaction("⬆")
    await message.add_reaction("⬇️")
    await message.add_reaction("▶")
    await message.add_reaction("⏩")
    # 時間の指定
    await message.add_reaction("🐔")
    await message.add_reaction("🌞")
    await message.add_reaction("🌙")

    # リアクションの待機
    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id

    try:
        while True:
            reaction, user = await bot.wait_for("reaction_add", timeout=120.0, check=check)
            last_date = calendar.monthrange(current_year, current_month)[1]

            # 月の変更を処理
            if str(reaction.emoji) == "⏪":
                current_month -= 1
                if current_month == 0:
                    current_month = 12
                    current_year -= 1
            elif str(reaction.emoji) == "⏩":
                current_month += 1
                if current_month == 13:
                    current_month = 1
                    current_year += 1
            # カレンダーの横移動を処理
            elif str(reaction.emoji) == "⬆️" and selected_date - 7 > 0:
                selected_date -= 7
            elif str(reaction.emoji) == "⬇️" and selected_date + 7 < last_date + 1:
                selected_date += 7
            elif str(reaction.emoji) == "◀" and selected_date - 1 > 0:
                selected_date -= 1
            elif str(reaction.emoji) == "▶" and selected_date + 1 < last_date + 1:
                selected_date += 1
            elif str(reaction.emoji) == "🐔":
                out = f"{current_year}-{current_month}-{selected_date} 08:00"
                await ctx.send(out)
                return out
            elif str(reaction.emoji) == "🌞":
                out = f"{current_year}-{current_month}-{selected_date} 13:00"
                await ctx.send(out)
                return out
            elif str(reaction.emoji) == "🌙":
                out = f"{current_year}-{current_month}-{selected_date} 18:00"
                await ctx.send(out)
                return out
            await reaction.message.remove_reaction(reaction, user)

            # カレンダーの内容を更新
            calendar_message, emoji = _create_calendar_message(
                current_month, current_year, selected_date
            )
            await message.edit(content=calendar_message)

    except asyncio.TimeoutError:
        await ctx.send("タイムアウトしました")
        return


def _create_calendar_message(month, year, selected_date=0):
    cal = calendar.monthcalendar(year, month)
    header = f"```\nカレンダー {year}年 {month}月\n"
    weekdays = [" Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_names = "  ".join([f"{weekday}" for weekday in weekdays])
    calendar_str = header + weekday_names + "\n"
    emoji = []
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "     "
                emoji.append(None)
            else:
                if day == selected_date and month == month and year == year:
                    week_str += f" [{day:2d}]"
                else:
                    week_str += f"  {day:2d} "
                emoji.append(f"{year}-{month:02}-{day:02}")
        calendar_str += week_str + "\n"
    calendar_str += "```"
    return calendar_str, emoji


# Discord botのトークンを使って起動
# bot.run(TOKEN)