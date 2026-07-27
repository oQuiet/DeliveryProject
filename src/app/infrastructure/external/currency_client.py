from decimal import Decimal
import json

import aiohttp


class CurrencyClient:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def fetch_currency(self, url: str) -> Decimal:
        async with self._session.get(url) as response:
            data = await response.json(
                content_type=None,
                loads=lambda s: json.loads(s, parse_float=Decimal),
            )
            return data["Valute"]["USD"]["Value"]
