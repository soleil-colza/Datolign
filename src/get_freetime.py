import discord
import os
from discord.ext import commands
import datetime
import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from select_date import select_date

load_dotenv()

# Google Calendar APIの設定
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLIENT_SECRET_FILE = "../token.json"
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"

# 日本時間のタイムゾーンを指定
jst = pytz.FixedOffset(540)


def get_free_time(
    start_date,
    end_date,
    interval_minutes,
    output_limit,
    except_start_time_msg,
    except_end_time_msg,
):
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

    except_start_time = ""
    except_end_time = ""
    except_date_str = start_date

    except_start_time = except_date_str.replace(
        hour=int(except_start_time_msg.content.split(":")[0]),
        minute=int(except_start_time_msg.content.split(":")[1]),
    )

    except_end_time = except_date_str.replace(
        hour=int(except_end_time_msg.content.split(":")[0]),
        minute=int(except_end_time_msg.content.split(":")[1]),
    )

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
        if current_time < event[0] and not (
            except_start_time.time() <= current_time.time() <= except_end_time.time()
        ):
            while current_time < event[0] and not (
                except_start_time.time() <= current_time.time() <= except_end_time.time()
            ):  # 〇時間ずつ空いている時間帯を追加
                next_time = current_time + datetime.timedelta(minutes=interval_minutes)
                if next_time <= event[0] and not (
                    except_start_time.time() <= next_time.time() <= except_end_time.time()
                ):  # 〇時間後の時間がイベント開始より前なら追加
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


# bot = commands.Bot(
#     command_prefix="!", intents=discord.Intents.all()
# )  # 好きなコマンドのプレフィックスを"!"に変更してください


# @bot.event
async def send_on_ready(bot):
    print(f"{bot.user.name} has connected to Discord!")


async def send_reaction_limit(bot, reaction, user):
    # リアクションが投票期日後に付けられたかを確認する
    if reaction.message.content.startswith("Proposed timeslot:"):
        deadline_str = reaction.message.content.split("at")[1].strip()
        deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        if datetime.datetime.utcnow() > deadline:
            # 現在の日付と時刻が投票期日を過ぎている場合、 そのことをユーザーに知らせるメッセージを表示する
            await reaction.message.channel.send(f"この投票の期限は{deadline_str}でした。.")
            # 期限が過ぎてから追加されたリアクションを削除する
            await reaction.remove(user)
        else:
            # 期日以前の投票は許可する　***ここの処理が重複しないように後ほど処理***
            print(f"{user} が {reaction.message.content} に {reaction.emoji}と投票しました！")


async def send_message(bot, message):
    # メッセージがbot自身のものであれば無視
    if message.author.bot:
        return

    # メンションのリスト（@botname または @botname#0000）
    mentions = [f"<@{bot.user.id}>", f"<@!{bot.user.id}>"]

    # メンションが含まれているかを確認
    if any(mention in message.content for mention in mentions):
        # メンションが含まれていれば、freetimeの処理を実行
        await process_freetime_command(bot, message)

    # コマンドの解析を行うために必要
    await bot.process_commands(message)


async def process_freetime_command(bot, message):
    await message.channel.send("さあ、検索を始めましょう！🔍 いつから探し始めるか教えてくださいね（例: 2023-08-01 12:00）")
    # start_date_msg = await bot.wait_for("message", check=lambda m: m.author == message.author)
    start_date_msg = await select_date(bot, message)

    await message.channel.send("そして、検索を終える日時はいつにしますか？📅（例: 2023-08-03 12:00）")
    # end_date_msg = await bot.wait_for("message", check=lambda m: m.author == message.author)
    end_date_msg = await select_date(bot, message)

    await message.channel.send("次に、検索をスキップする開始時間を教えてください。⏰（例: 00:00）")
    except_start_time_msg = await bot.wait_for(
        "message", check=lambda m: m.author == message.author
    )

    await message.channel.send("同様に、検索をスキップする終了時間も教えてくださいね。⏰（例: 09:00）")
    except_end_time_msg = await bot.wait_for("message", check=lambda m: m.author == message.author)

    await message.channel.send("表示間隔は何分にしますか？⏳（例: 60）")
    interval_minutes_msg = await bot.wait_for("message", check=lambda m: m.author == message.author)

    await message.channel.send("表示したい件数は何件にしますか？🔢（例: 5）")
    output_limit_msg = await bot.wait_for("message", check=lambda m: m.author == message.author)

    try:
        start_date = jst.localize(datetime.datetime.strptime(start_date_msg, "%Y-%m-%d %H:%M"))
        end_date = jst.localize(datetime.datetime.strptime(end_date_msg, "%Y-%m-%d %H:%M"))
        interval_minutes = int(interval_minutes_msg.content)
        output_limit = int(output_limit_msg.content)

    except ValueError:
        await message.channel.send("おっと、入力がちょっと違うみたいです。😅 正しい形式で再度入力してみてくださいね。")
        await message.channel.send("大丈夫、一度リセットして最初からやり直しましょう。🔄")
        return

    free_time_slots = get_free_time(
        start_date,
        end_date,
        interval_minutes,
        output_limit,
        except_start_time_msg,
        except_end_time_msg,
    )

    error_flag = False

    if except_start_time_msg.content > except_end_time_msg.content:
        await message.channel.send("検索をスキップする終了時間は、検索をスキップする開始時間より後に設定してね。")
        error_flag = True

    if start_date > end_date:
        await message.channel.send("ちょっと待って、終了日時は開始日時より後に設定する必要がありますよ。⏰")
        error_flag = True

    if free_time_slots == []:
        await message.channel.send("ごめんなさい、指定された期間に空いている時間帯が見つかりませんでした。😔")
        error_flag = True

    if error_flag:
        await message.channel.send("もう一度最初から始めましょう！")
        return

    output = ""
    for slot in free_time_slots:
        # 日本時間に変換して送信
        start_time_jst = slot[0].astimezone(jst).strftime("%Y-%m-%d %H:%M")
        end_time_jst = slot[1].astimezone(jst).strftime("%Y-%m-%d %H:%M")
        output = f"{start_time_jst} から {end_time_jst}\n"
        sent_message = await message.channel.send("```" + output + "```")

        # メッセージに対してリアクションを追加
        await sent_message.add_reaction("👍")
        await sent_message.add_reaction("👀")
        await sent_message.add_reaction("🎉")

        # 投票期限（＝start_date_msg）の取得
    deadline = start_date_msg

    # 投票期限の表示
    await message.channel.send(f"投票期限は: {deadline} だよ！")


# @bot.event
async def check_reaction(bot, reaction, user):
    # リアクションがBot自身によるものであれば無視
    if user == bot.user:
        return

    if str(reaction.emoji) in ["👍", "👀", "🎉"]:
        for react in reaction.message.reactions:
            if str(react) != str(reaction.emoji):
                await reaction.message.remove_reaction(react, user)


# Discord botのトークンを使って起動
# bot.run(os.getenv('TOKEN'))
