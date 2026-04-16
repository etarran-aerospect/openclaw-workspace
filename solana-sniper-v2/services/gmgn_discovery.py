import json
import threading
import time
import uuid
from typing import List, Optional
from urllib import parse, request
from urllib.error import HTTPError


GMGN_DEFAULT_HOST = "https://openapi.gmgn.ai"
TRENCHES_DEFAULT_PLATFORMS = {
    "sol": ["Pump.fun", "letsbonk"],
}
TRENCHES_DEFAULT_QUOTE_ADDRESS_TYPES = {
    "sol": [4, 5, 3, 1, 13, 0],
}


class GmgnDiscovery:
    def __init__(self, api_key: str, chain: str = "sol", timeout: int = 20, host: str = GMGN_DEFAULT_HOST):
        self.api_key = api_key
        self.chain = chain
        self.timeout = timeout
        self.host = host.rstrip("/")
        self._lock = threading.Lock()
        self._pending: List[dict] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._seen_items = set()
        self._stats = {
            "poll_attempts": 0,
            "http_errors": 0,
            "items_seen": 0,
            "new_items": 0,
            "duplicates": 0,
            "decode_fail": 0,
            "last_error": "",
            "last_result_count": 0,
            "mode": "openapi_trenches_v2_multi_bucket",
        }

    def start(self, poll_interval_seconds: int = 10):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            args=(poll_interval_seconds,),
            daemon=True,
            name="gmgn-discovery",
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def pop_pending_candidates(self) -> List[dict]:
        with self._lock:
            items = list(self._pending)
            self._pending.clear()
        return items

    def get_stats(self) -> dict:
        return dict(self._stats)

    def _poll_loop(self, interval_seconds: int):
        while not self._stop.is_set():
            try:
                self.poll_once()
            except Exception as e:
                self._stats["http_errors"] += 1
                self._stats["last_error"] = str(e)
            self._stop.wait(interval_seconds)

    def poll_once(self):
        self._stats["poll_attempts"] += 1
        self._stats["last_error"] = ""

        items = []
        for item in self._fetch_trenches():
            normalized = self._normalize_item(item)
            if not normalized:
                self._stats["decode_fail"] += 1
                continue
            items.append(normalized)

        self._stats["last_result_count"] = len(items)
        self._stats["items_seen"] += len(items)

        for normalized in items:
            dedupe_key = (
                normalized["token_address"],
                normalized.get("gmgn_bucket", ""),
                int(normalized.get("created_timestamp") or 0),
                int(normalized.get("open_timestamp") or 0),
            )
            if dedupe_key in self._seen_items:
                self._stats["duplicates"] += 1
                continue
            self._seen_items.add(dedupe_key)
            with self._lock:
                self._pending.append(normalized)
            self._stats["new_items"] += 1

        if not items and not self._stats["last_error"]:
            self._stats["last_error"] = "GMGN returned no discovery items"

    def _auth_query(self, params: dict) -> dict:
        query = dict(params)
        query["timestamp"] = str(int(time.time()))
        query["client_id"] = str(uuid.uuid4())
        return query

    def _fetch_json(self, method: str, path: str, params: dict, body: Optional[dict] = None):
        query = self._auth_query(params)
        url = f"{self.host}{path}?{parse.urlencode(query, doseq=True)}"
        payload = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(
            url,
            data=payload,
            method=method,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "X-APIKEY": self.api_key,
            },
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                response_text = resp.read().decode("utf-8")
                parsed = json.loads(response_text)
        except HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8", "ignore")
            except Exception:
                pass
            detail = f"HTTP {e.code}: {e.reason}"
            if body_text:
                detail += f" body={body_text[:300]}"
            raise RuntimeError(detail)
        if isinstance(parsed, dict) and parsed.get("code") not in (0, None):
            raise RuntimeError(
                f"GMGN error code={parsed.get('code')} error={parsed.get('error')} message={parsed.get('message')}"
            )
        return parsed.get("data") if isinstance(parsed, dict) and "data" in parsed else parsed

    def _fetch_trenches(self):
        body = self._build_trenches_body()
        try:
            data = self._fetch_json("POST", "/v1/trenches", {"chain": self.chain}, body)
        except Exception as e:
            self._stats["http_errors"] += 1
            self._stats["last_error"] = f"trenches -> {e}"
            return []
        out = []
        mapping = {
            "new_creation": "new_creation",
            "near_completion": "near_completion",
            "completed": "completed",
        }
        for data_key, bucket in mapping.items():
            values = (data or {}).get(data_key) or []
            if isinstance(values, list):
                for item in values:
                    row = dict(item)
                    row["_gmgn_bucket"] = bucket
                    out.append(row)
        return out

    def _build_trenches_body(self) -> dict:
        launchpads = TRENCHES_DEFAULT_PLATFORMS.get(self.chain, [])
        quote_types = TRENCHES_DEFAULT_QUOTE_ADDRESS_TYPES.get(self.chain, [])
        section = {
            "filters": ["offchain", "onchain"],
            "launchpad_platform": launchpads,
            "quote_address_type": quote_types,
            "launchpad_platform_v2": True,
            "limit": 80,
        }
        return {
            "version": "v2",
            "new_creation": dict(section),
            "near_completion": dict(section),
            "completed": dict(section),
        }

    @staticmethod
    def _normalize_item(item: dict):
        if not isinstance(item, dict):
            return None
        token = item.get("address") or item.get("token_address") or item.get("base_address") or item.get("base_mint") or item.get("ca")
        if not token:
            return None
        liquidity_usd = float(item.get("liquidity") or 0)
        fdv_usd = float(item.get("market_cap") or item.get("usd_market_cap") or 0)
        progress_raw = item.get("progress") or 0
        progress_pct = float(progress_raw) * 100 if float(progress_raw) <= 1 else float(progress_raw)
        return {
            "token_address": token,
            "pair_address": item.get("pool_address") or item.get("pair_address") or item.get("address") or "",
            "symbol": item.get("symbol") or item.get("base_symbol") or "",
            "name": item.get("name") or item.get("base_name") or "",
            "gmgn_raw": item,
            "pool_source": "gmgn_openapi_trenches",
            "source_url": item.get("_gmgn_bucket") or "trenches",
            "gmgn_bucket": item.get("_gmgn_bucket") or "unknown",
            "launchpad_platform": item.get("launchpad_platform") or item.get("launchpad") or "",
            "liquidity_usd": liquidity_usd,
            "fdv_usd": fdv_usd,
            "holder_count": int(item.get("holder_count") or 0),
            "rug_ratio": float(item.get("rug_ratio") or 0),
            "bundler_rate": float(item.get("bundler_trader_amount_rate") or item.get("bundler_rate") or 0),
            "top_10_holder_rate": float(item.get("top_10_holder_rate") or 0),
            "smart_degen_count": int(item.get("smart_degen_count") or 0),
            "renowned_count": int(item.get("renowned_count") or 0),
            "has_socials": bool(item.get("has_at_least_one_social")),
            "owner_renounced": str(item.get("owner_renounced") or "").lower() in ("yes", "true", "1"),
            "creator_token_status": item.get("creator_token_status") or "",
            "created_timestamp": int(item.get("created_timestamp") or 0),
            "open_timestamp": int(item.get("open_timestamp") or 0),
            "progress_pct": progress_pct,
        }
