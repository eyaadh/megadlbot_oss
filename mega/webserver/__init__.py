"""web server to serve telegram files as Partial content or full content for streaming."""
from aiohttp import web
from mega.webserver.routes import routes


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app
