import discord
import os
from dotenv import load_dotenv
from multiprocessing.connection import Connection

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")


@client.event
async def on_message(msg: discord.Message) -> None:
    if msg.author == client.user:
        return

    if msg.content.startswith("$hello"):
        await msg.channel.send(f"hello, {msg.author}")


def main(pipe_end: Connection) -> None:
    a = pipe_end.recv()
    print(a)
    if type(BOT_TOKEN) is str:
        client.run(BOT_TOKEN)
