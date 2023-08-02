import dotenv
import os
import discord

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))
client = discord.Client()
client.run(token)