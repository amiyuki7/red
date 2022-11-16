from .lib import cube
from multiprocessing.connection import Connection

from sanic import Request, Sanic
from sanic.response import text

app = Sanic(name="bot")


@app.get("/")
async def hello_world(_: Request):
    return text(f"Hello world! 4^3 = {cube(4)}")


def main(pipe_end: Connection):
    pipe_end.send("Hello from sanic server (redqct)")
    app.run(host="127.0.0.1", port=8080, debug=True)
