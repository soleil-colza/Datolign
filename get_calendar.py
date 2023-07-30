import discord
from discord.ext import commands
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Googleカレンダーの読み取り専用スコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN = ""

bot = commands.Bot(
    command_prefix="!", intents=discord.Intents.all()
)  # 好きなコマンドのプレフィックスを"!"に変更してください


def get_google_calendar_events():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        return events
    except HttpError as error:
        print("エラーが発生しました: %s" % error)
        return None


@bot.command()
async def 予定(ctx):
    events = get_google_calendar_events()
    if not events:
        await ctx.send("予定はありません。")
        return

    upcoming_events_msg = "次の10件の予定:\n"
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event["summary"]
        upcoming_events_msg += f"{start}: {summary}\n"

    await ctx.send(upcoming_events_msg)


@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user.name}")
    print("------")


# 'YOUR_DISCORD_BOT_TOKEN'をあなたのボットトークンに置き換えてください
bot.run(TOKEN)
