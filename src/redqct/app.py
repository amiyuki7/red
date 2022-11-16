from multiprocessing import Process, Pipe

from .bot import main as client_main
from .server import main as server_main

client_end, server_end = Pipe()

client_proc = Process(
    target=client_main,
    args=(client_end,),
)

server_proc = Process(
    target=server_main,
    args=(server_end,),
)

if __name__ == "__main__":
    client_proc.start()
    server_proc.start()
    client_proc.join()
    server_proc.join()
