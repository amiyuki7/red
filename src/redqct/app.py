import asyncio
import discord
import os
from dotenv import load_dotenv
from discord.ext.commands import Bot, Context
from fastapi import FastAPI
from .lib import cube

load_dotenv()
# Set this in .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
# BOT_TOKEN = os.getenv("DEV_TOKEN")
assert type(BOT_TOKEN) is str


server = FastAPI()

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix="$", intents=intents)


@server.get("/")
async def root_route():
    return {"cube of 4": cube(4)}


@server.get("/kanye")
async def kanye_route():
    await bot.get_channel(1042389563009683496).send("Somebody just did a GET request @ 127.0.0.1:8000/kanye")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def kanye(ctx: Context):
    await ctx.send(f"{ctx.author.display_name} thinks that kanye is king :crown:")


async def main():
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()


asyncio.create_task(main())
