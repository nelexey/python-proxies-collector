from datetime import datetime
import json
import re
import asyncio
import aiohttp

from .checker import ipify


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


# async def fetch_json(session, url):
#     async with session.get(url) as response:
#         if response.status == 200:
#             data = await response.json()
#             return data

async def fetch_json(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if content_type == 'application/json':
                try:
                    data = await response.json()
                    return data
                except json.JSONDecodeError:
                    return ""
            else:
                # Если MIME-тип не application/json, попытаемся распарсить текст как JSON
                text = await response.text()
                try:
                    data = json.loads(text)
                    return data
                except json.JSONDecodeError:
                    return ""
        else:
            # Если статус не 200, вернем пустую строку
            return ""

async def parser1():
    url = 'https://free-proxy-list.net/'
    regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}"

    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, url)

        matches = re.finditer(regex, page_content, re.MULTILINE)

        proxies_list = [match.group() for match in matches]

        working_proxies = await ipify(proxies_list)

        proxies_count = len(proxies_list)

        return url, working_proxies, proxies_count


async def parser2():
    url = 'https://proxycompass.com/wp-admin/admin-ajax.php?action=proxylister_download&nonce=0c0ad340aa&format=json&filter={}'

    async with aiohttp.ClientSession() as session:
        page_content = await fetch_json(session, url)

        proxies_list = []

        for item in page_content:
            ip = item.get('ip_address')
            port = item.get('port')
            if ip and port:
                proxy = f"{ip}:{port}"
                proxies_list.append(proxy)

        working_proxies = await ipify(proxies_list)

        proxies_count = len(proxies_list)

        return url, working_proxies, proxies_count


async def parser3():
    proxies_list = []
    working_proxies = []
    proxies_count = 0

    async with aiohttp.ClientSession() as session:
        for page in range(1, 16):
            url = f"https://www.proxyshare.com/detection/proxyList?limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
            try:
                page_content = await fetch_json(session, url)
                if page_content and isinstance(page_content, dict) and 'data' in page_content and page_content['data']:
                    for item in page_content['data']:
                        ip = item.get('ip')
                        port = item.get('port')
                        if ip and port:
                            proxy = f"{ip}:{port}"
                            proxies_list.append(proxy)
                            print(page, proxy)
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    print(f"Ошибка 404 на странице {page}. Прекращаем перебор.")
                    break
                else:
                    print(f"Ошибка при получении данных со страницы {page}. Статус код: {e.status}")

        working_proxies = await ipify(proxies_list)
        proxies_count = len(proxies_list)

    return url, working_proxies, proxies_count

async def parser4():
    url = "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json"

    async with aiohttp.ClientSession() as session:
        page_content = await fetch_json(session, url)

        proxies_list = []

        if page_content:
            for protocol in ['http', 'https']:
                if protocol in page_content:
                    proxies_list.extend(page_content[protocol])

        working_proxies = await ipify(proxies_list)

        proxies_count = len(proxies_list)

        return url, working_proxies, proxies_count

async def collect(count: int | None = None, filename: str = 'proxies_list', frmt='json'):
    proxies_list = []
    tasks = []

    async def log_proxies(url, working, all_proxies):
        print(f'{url:20} | {working}/{all_proxies} working proxies...')

    if count is not None:
        for name, parser in sites_parsers.items():
            if len(proxies_list) >= count:
                break
            url, working_proxies, proxies_count = await parser()
            proxies_list += working_proxies
            await log_proxies(url, len(working_proxies), proxies_count)
    else:
        for name, parser in sites_parsers.items():
            url, working_proxies, proxies_count = await parser()
            proxies_list += working_proxies
            await log_proxies(url, len(working_proxies), proxies_count)

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_json = {
        'count': len(proxies_list),
        'last_updated': last_updated,
        'proxies_list': proxies_list,
    }

    print('End of checking, waiting for restart...')

    return await asyncio.to_thread(write_to_file, f'source/data/{filename}.{frmt}', output_json)

# async def collect(count: int | None = None, filename: str = 'proxies_list', frmt='json'):
#     proxies_list = []
#     tasks = []
#
#     async def log_proxies(url, working, all_proxies):
#         return print(f'{url:20} | {working}/{all_proxies} working proxies...')
#
#     if count is not None:
#         for name, parser in sites_parsers.items():
#             if len(proxies_list) >= count: break
#             url, working_proxies, proxies_count = await parser()
#             proxies_list += working_proxies
#             await log_proxies(url, len(working_proxies), proxies_count)
#     else:
#         for name, parser in sites_parsers.items():
#             url, working_proxies, proxies_count = await parser()
#             proxies_list += working_proxies
#             await log_proxies(url, len(working_proxies), proxies_count)
#
#     last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     output_json = {
#         'count': len(proxies_list),
#         'last_updated': last_updated,
#         'proxies_list': proxies_list,
#     }
#
#     print('End of checking, waiting for restart...')
#
#     return await asyncio.to_thread(write_to_file, f'source/data/{filename}.{frmt}', output_json)
#

def write_to_file(filename, data):
    # This function runs in a separate thread
    with open(filename, 'w') as file:
        json.dump(data, file)


sites_parsers = {
    'free-proxy-list.net': parser1,
    'proxycompass.com': parser2,
    'proxiware.com': parser3,
    'githubproxy': parser4,
    # 'openproxy.space': parser5,
    # 'proxycompass.com': parser6,
}
