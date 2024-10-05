from aiohttp import web
import asyncio
import traceback
import json


async def ppxc_list(request):
    try:
        # Read the JSON file
        with open('source/data/proxies_list.json', 'r') as file:
            data = json.load(file)

        # Return the JSON data as a response
        return web.json_response(data)

    except Exception as e:
        traceback.print_exc()
        return web.Response(text="Error processing request", status=500)

async def ppxc(request):
    try:
        return web.Response(text='OK')
    except Exception as e:
        traceback.print_exc()
        return web.Response(text="Error processing request", status=500)




