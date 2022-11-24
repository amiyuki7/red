import asyncio
import aiohttp
from typing import List, Tuple


async def fetch_bytes(session: aiohttp.ClientSession, url: str, id: str) -> Tuple[bytes, str]:
    async with session.get(url) as response:
        # Debug
        print(response.status, response.content_type)
        bytes = await response.read()
        return (bytes, id)


async def fetch_all(pairs: List[Tuple[str, str]]) -> List[Tuple[bytes, str]]:
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch_bytes(session, *pair) for pair in pairs])
        return results
