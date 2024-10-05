import asyncio
import aiohttp


async def fetch(session, proxy, url):
    try:
        async with session.get(url=url, proxy=f'http://{proxy}', timeout=3) as response:
            result_ip = await response.text()
            print(f"Proxy: {proxy} - Result: {result_ip}")
            return proxy  # Сохраняем рабочий прокси
    except Exception as e:
        print(f"Proxy: {proxy} - Error: {e}")
        return None


async def ipify(proxies: list, batch_size: int = 1000):
    url = 'https://api.ipify.org'
    working_proxies = []

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(batch_size)

        async def bound_fetch(proxy):
            async with semaphore:
                result = await fetch(session, proxy, url)
                if result:
                    working_proxies.append(result)

        tasks = [bound_fetch(proxy) for proxy in proxies]
        await asyncio.gather(*tasks)

    return working_proxies


# Пример использования
if __name__ == "__main__":
    proxy_list = [
        'proxy1:port',
        'proxy2:port',
        'proxy3:port',
        # Добавьте сюда ваши прокси
    ]

    loop = asyncio.get_event_loop()
    working = loop.run_until_complete(ipify(proxy_list, batch_size=5))
    print("Рабочие прокси:", working)


# import asyncio
# import aiohttp
#
# async def fetch(session, proxy, url):
#
#     try:
#         async with session.get(url=url, proxy=f'http://{proxy}', timeout=1) as response:
#             result_ip = await response.text()
#             print(result_ip)
#             return result_ip
#     except Exception as e:
#         print(e)
#         return None
#
# async def ipify(proxies: list, batch_size: int = 10):
#     url = 'https://api.ipify.org'
#     working_proxies = []
#
#     async with aiohttp.ClientSession() as session:
#         for i in range(0, len(proxies), batch_size):
#             batch = proxies[i:i+batch_size]
#             for proxy in batch:
#                 if p := await fetch(session, proxy, url) == proxy:
#                     working_proxies.append(proxy)
#
#
#     return working_proxies
