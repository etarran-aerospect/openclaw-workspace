import requests


class PolymarketGammaClient:
    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def active_markets(self, limit: int = 50, offset: int = 0):
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit,
            "offset": offset,
        }
        r = requests.get(f"{self.BASE_URL}/markets", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def event_by_slug(self, slug: str):
        r = requests.get(f"{self.BASE_URL}/events", params={"slug": slug}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
