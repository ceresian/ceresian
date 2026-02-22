from typing import Any

import httpx

from .config import get_settings


class TMDBClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.tmdb_api_key
        self.base_url = settings.tmdb_base_url

    async def search_movies(self, query: str) -> list[dict[str, Any]]:
        if not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.base_url}/search/movie",
                params={"api_key": self.api_key, "query": query},
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("results", [])
