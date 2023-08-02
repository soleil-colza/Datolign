import discord
from discord.ext import commands
import datetime
import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Google Calendar APIの設定
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLIENT_SECRET_FILE = "token.json"
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"
TOKEN = ""

# 日本時間のタイムゾーンを指定
jst = pytz.timezone("Asia/Tokyo")


def get_free_time(start_date, end_date, interval_minutes, output_limit):
    creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE, SCOPES)
    service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)

    # 日本時間を使用
    utc = pytz.timezone("UTC")

    # イベントリストの取得
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_date.astimezone(utc).isoformat(),
            timeMax=end_date.astimezone(utc).isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    busy_slots = []
    for event in events:
        start = event["start"].get("dateTime")
        end = event["end"].get("dateTime")
        # 終日の予定の場合はstartとendが存在しないので、all_dayに開始日時を代入
        all_day = event.get("start").get("date") if event.get("start") else None
        if not all_day and start and end:
            busy_slots.append(
                (
                    datetime.datetime.fromisoformat(start),
                    datetime.datetime.fromisoformat(end),
                )
            )

    # 空いている時間帯を計算
    free_slots = []
    current_time = start_date
    for event in busy_slots:
        if current_time < event[0]:
            while current_time < event[0]:  # 〇時間ずつ空いている時間帯を追加
                next_time = current_time + datetime.timedelta(minutes=interval_minutes)
                if next_time <= event[0]:  # 〇時間後の時間がイベント開始より前なら追加
                    free_slots.append((current_time, next_time))
                current_time = next_time
        current_time = event[1]

    # 最後のイベント終了後の時間帯を追加
    if current_time < end_date:
        while current_time < end_date:
            next_time = current_time + datetime.timedelta(minutes=interval_minutes)
            if next_time <= end_date:  # 〇時間後の時間が終了日時より前なら追加
                free_slots.append((current_time, next_time))
            current_time = next_time

    free_slots = free_slots[:output_limit]  # output_limitの数だけ返す
    return free_slots


bot = commands.Bot(
    command_prefix="!", intents=discord.Intents.all()
)  # 好きなコマンドのプレフィックスを"!"に変更してください


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.command()
async def freetime(ctx):
    await ctx.send("検索開始日時を指定してください。（例: 2023-08-01 12:00）")
    start_date_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author
    )

    await ctx.send("検索終了日時を指定してください。（例: 2023-08-03 12:00）")
    end_date_msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author)

    await ctx.send("表示間隔（分）を指定してください。（例: 60）")
    interval_minutes_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author
    )

    await ctx.send("表示数を指定してください。（例: 5）")
    output_limit_msg = await bot.wait_for(
        "message", check=lambda m: m.author == ctx.author
    )

    try:
        start_date = jst.localize(
            datetime.datetime.strptime(start_date_msg.content, "%Y-%m-%d %H:%M")
        )
        end_date = jst.localize(
            datetime.datetime.strptime(end_date_msg.content, "%Y-%m-%d %H:%M")
        )
        interval_minutes = int(interval_minutes_msg.content)
        output_limit = int(output_limit_msg.content)
    except ValueError:
        await ctx.send("入力が無効です。正しい形式で入力してください。")
        await ctx.send("もう一度初めからやり直してください。")
        return

    free_time_slots = get_free_time(
        start_date, end_date, interval_minutes, output_limit
    )

    if start_date > end_date:
        await ctx.send("終了日時は開始日時より後に設定してください。")
        return

    if free_time_slots == []:
        await ctx.send("指定された期間に空いている時間帯はありません。")
        return

    output = ""
    for slot in free_time_slots:
        # 日本時間に変換して送信
        start_time_jst = slot[0].astimezone(jst).strftime("%Y-%m-%d %H:%M")
        end_time_jst = slot[1].astimezone(jst).strftime("%Y-%m-%d %H:%M")
        output = f"{start_time_jst} から {end_time_jst}\n"
        await ctx.send("```" + output + "```")


# Discord botのトークンを使って起動
bot.run(TOKEN)
