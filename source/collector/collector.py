import contextlib
import json
import requests
import re
import asyncio
import aiohttp
import cloudscraper

from .checker import ipify


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def fetch_file(session, url):
    filename = 'sites_data.json'
    scraper = cloudscraper.create_scraper()

    with session.get(url) as response:
        assert response.status == 200
        with open(filename, "wb") as f:
            while True:
                chunk = await response.content.readany()
                if not chunk:
                    break
                f.write(chunk)




async def parser1():
    url = 'https://free-proxy-list.net/'
    regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}"

    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, url)

        matches = re.finditer(regex, page_content, re.MULTILINE)

        proxies_list = [match.group() for match in matches]

        working_proxies = await ipify(proxies_list)

        return working_proxies


async def parser2():
    url = 'https://proxycompass.com/'
    regex = r'"ajax_url":"(.*?)".*?"nonce":"(.*?)"'

    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, url)

        match = re.search(regex, page_content, re.MULTILINE)

        download_url = f'https://proxycompass.com/wp-admin/admin-ajax.php?nonce={match.group(2)}'

        print(download_url)

        file_content = await fetch_file(session, download_url)

        print(file_content)

        return

        proxies_list = [match.group() for match in matches]

        working_proxies = await ipify(proxies_list)

        return working_proxies


async def parser3():
    url = 'https://proxiware.com/'
    regex = r"<td class=\"table-ip\">(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td>(\d{2,5})</td>"

    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, url)

        matches = re.findall(regex, page_content)

        proxies_list = [match.group() for match in matches]

        working_proxies = await ipify(proxies_list)

        return working_proxies


async def collect():
    proxies_list = []
    tasks = []

    for name, parser in sites_parsers.items():
        # Add tasks for the parsers to be run asynchronously
        proxies_list.append(await parser())  # Pass name if necessary

    print(proxies_list)

    # Writing the result to a file
    # Use asyncio.to_thread to run the blocking file I/O in a separate thread
    return await asyncio.to_thread(write_to_file, 'source/data/proxies_list.json', proxies_list)


def write_to_file(filename, data):
    # This function runs in a separate thread
    with open(filename, 'w') as file:
        json.dump(data, file)


sites_parsers = {
    'free-proxy-list.net': parser1,
    # 'proxycompass.com': parser2,
    # 'proxiware.com': parser3,
    # 'proxynova.com': parser4,
    # 'openproxy.space': parser5,
    # 'proxycompass.com': parser6,
}
