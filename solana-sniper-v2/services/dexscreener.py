import requests


class DexScreenerClient:
    BASE_URL = "https://api.dexscreener.com"

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def latest_token_profiles(self):
        r = requests.get(f"{self.BASE_URL}/token-profiles/latest/v1", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def token_pairs(self, token_address: str):
        r = requests.get(
            f"{self.BASE_URL}/token-pairs/v1/solana/{token_address}",
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def latest_pairs_for_token(self, token_address: str):
        r = requests.get(
            f"{self.BASE_URL}/latest/dex/tokens/{token_address}",
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json().get("pairs", [])
