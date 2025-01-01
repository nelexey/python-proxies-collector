from aiohttp import web
import traceback
import json
import aiohttp

from ..collector.checker import fetch

async def ppxc_list(request):
    try:
        with open('source/data/proxies_list.json', 'r') as file:
            data = json.load(file)

        return web.json_response(data)

    except Exception as e:
        traceback.print_exc()
        return web.Response(text="Error processing request", status=500)

async def ppxc(request):
    try:
        with open('source/data/proxies_list.json', 'r') as file:
            data = json.load(file)
        

        async with aiohttp.ClientSession() as session:
            for proxy in data['proxies_list']:
                if await fetch(session, proxy, 'https://api.ipify.org'):
                    return web.Response(text=proxy, status=200)
        
        return web.Response(text="No working proxies available", status=503)
    except Exception as e:
        traceback.print_exc()
        return web.Response(text="Error processing request", status=500)