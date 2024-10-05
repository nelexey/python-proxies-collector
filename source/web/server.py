from aiohttp import web
from .urls import urls

class WebServer:
    def __init__(self, config: dict):
        self.config = config
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        for route in urls:
            self.app.router.add_route(route['method'], route['path'], route['handler'])

    async def run(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.config['host'], self.config['port'],
                           shutdown_timeout=self.config['timeout'],
                           backlog=self.config['max_connections'])
        await site.start()


async def init_web_server(config: dict):
    server = WebServer(config)
    await server.run()