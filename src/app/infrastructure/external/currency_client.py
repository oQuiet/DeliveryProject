from decimal import Decimal
import json

import aiohttp
from redis.asyncio import Redis


class CurrencyClient:
    CACHE_KEY = "usd_rub"

    def __init__(self, redis: Redis, url: str) -> None:
        self.redis = redis
        self.url = url

    async def update_currency(self) -> Decimal:
        async with aiohttp.ClientSession() as session, session.get(self.url) as response:
            data = await response.json(
                content_type=None,
                loads=lambda s: json.loads(s, parse_float=Decimal),
            )

            rate = data["Valute"]["USD"]["Value"]
            await self.redis.set(self.CACHE_KEY, str(rate), ex=3900)

            return Decimal(rate)

    async def fetch_currency(self) -> Decimal:
        cached_rate = await self.redis.get(self.CACHE_KEY)

        if cached_rate is not None:
            return Decimal(cached_rate)  # type: ignore
        return await self.update_currency()
