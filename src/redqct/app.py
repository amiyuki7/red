import asyncio

from fastapi import FastAPI
from .lib import cube
from .bot import bot, main


server = FastAPI()


@server.get("/")
async def root_route():
    return {"cube of 4": cube(4)}


@server.get("/kanye")
async def kanye_route():
    await bot.get_channel(1042389563009683496).send("Somebody just did a GET request @ 127.0.0.1:8000/kanye")


asyncio.create_task(main())
