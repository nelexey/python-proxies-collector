import asyncio
import logging

from .misc import settings
from .web import init_web_server
from .collector import collect


async def run_collector():
    """
    Собирает прокси,
    сохраняет в файл,
    ждёт время.
    """

    while True:
        await collect()
        await asyncio.sleep(120) # 2 min


async def run_server():
    """
    Запускает сервер,
    обеспечивает корректное прерывание.
    """

    web_server_task = asyncio.create_task(init_web_server(settings.web_config))
    try:
        while True:
            await asyncio.sleep(3600) # 1 hour
    except KeyboardInterrupt:
        web_server_task.cancel()
        try:
            await web_server_task
        except asyncio.CancelledError:
            pass


def launch():
    loop = asyncio.get_event_loop()

    loop.run_until_complete(asyncio.gather(run_server(), run_collector()))
