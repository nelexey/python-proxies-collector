import asyncio
import logging

from .misc import settings
from .web import init_web_server
from .collector import collect



async def run_collector():
    while True:
        await collect()
        await asyncio.sleep(300) # 5 min

async def run_server():
    web_server_task = asyncio.create_task(init_web_server(settings.web_config))
    # This is a simple way of keeping the server running forever.
    try:
        while True:
            await asyncio.sleep(3600)  # Wait for one hour before checking again
    except KeyboardInterrupt:
        web_server_task.cancel()
        try:
            await web_server_task
        except asyncio.CancelledError:
            pass

def launch():
    # Создаем event loop
    loop = asyncio.get_event_loop()

    # Запускаем асинхронные функции одновременно
    loop.run_until_complete(asyncio.gather(run_server(), run_collector()))
