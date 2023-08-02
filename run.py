import discord
import os
from dotenv import load_dotenv

load_dotenv() 
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx): 
    await ctx.respond("Hey!")

@bot.slash_command(name="event", description="Create a new event with suggested timeslots")
async def event(ctx, date: str, duration: int):
    # Call Google Calendar API to fetch available timeslots based on the provided date and duration
    # This part is quite complicated and requires authorization, so we just simulate it here
    timeslots = ["10:00", "14:00", "16:00"]
    
    # Send these timeslots to the channel and add reactions for voting
    for timeslot in timeslots:
        msg = await ctx.respond(f"Proposed timeslot: {date} at {timeslot}")
        await msg.add_reaction("🎉")
        await msg.add_reaction("👀")
        await msg.add_reaction("👍")

@bot.event
async def on_reaction_add(reaction, user):
    # We can consider the added reaction as a vote here
    # You would need to add your own logic to count the votes and choose the best timeslot
    print(f"{user} voted for {reaction.message.content} with {reaction.emoji}")

bot.run(os.getenv('TOKEN')) # run the bot with the token
