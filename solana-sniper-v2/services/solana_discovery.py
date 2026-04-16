import base64
import json
import struct
import threading
from typing import List, Optional
from urllib import request


RAYDIUM_AMM_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
OPENBOOK_MARKET = "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"
WSOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class SolanaPoolDiscovery:
    LIQUIDITY_STATE_V4_SIZE = 752
    OFFSET_STATUS = 0
    OFFSET_POOL_OPEN_TIME = 224
    OFFSET_BASE_MINT = 400
    OFFSET_QUOTE_MINT = 432
    OFFSET_MARKET_PROGRAM_ID = 560

    def __init__(self, rpc_http_url: str, quote_mint: str = WSOL_MINT, timeout: int = 20):
        self.rpc_http_url = rpc_http_url
        self.quote_mint = quote_mint
        self.timeout = timeout
        self._lock = threading.Lock()
        self._pending: List[dict] = []
        self._seen_pool_accounts = set()
        self._poll_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._stats = {
            "poll_attempts": 0,
            "rpc_errors": 0,
            "accounts_seen": 0,
            "new_pools": 0,
            "duplicate_pools": 0,
            "wrong_quote_mint": 0,
            "wrong_market_program": 0,
            "bad_status": 0,
            "decode_fail": 0,
            "last_result_count": 0,
            "last_error": "",
        }

    def start(self, poll_interval_seconds: int = 15):
        if self._poll_thread and self._poll_thread.is_alive():
            return
        self._stop.clear()
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            args=(poll_interval_seconds,),
            daemon=True,
            name="solana-pool-discovery",
        )
        self._poll_thread.start()

    def stop(self):
        self._stop.set()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=2)

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
                self._stats["last_error"] = ""
            except Exception as e:
                self._stats["rpc_errors"] += 1
                self._stats["last_error"] = str(e)
            self._stop.wait(interval_seconds)

    def poll_once(self):
        self._stats["poll_attempts"] += 1
        filters = [
            {"dataSize": self.LIQUIDITY_STATE_V4_SIZE},
            {
                "memcmp": {
                    "offset": self.OFFSET_QUOTE_MINT,
                    "bytes": self.quote_mint,
                }
            },
            {
                "memcmp": {
                    "offset": self.OFFSET_MARKET_PROGRAM_ID,
                    "bytes": OPENBOOK_MARKET,
                }
            },
            {
                "memcmp": {
                    "offset": self.OFFSET_STATUS,
                    "bytes": self._encode_u64_le_base58(6),
                }
            },
        ]
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getProgramAccounts",
            "params": [
                RAYDIUM_AMM_V4,
                {
                    "encoding": "base64",
                    "filters": filters,
                },
            ],
        }
        data = self._rpc(payload)
        accounts = data.get("result") or []
        self._stats["last_result_count"] = len(accounts)
        self._stats["accounts_seen"] += len(accounts)

        for item in accounts:
            pubkey = item.get("pubkey")
            if not pubkey:
                continue
            if pubkey in self._seen_pool_accounts:
                self._stats["duplicate_pools"] += 1
                continue
            encoded = (((item.get("account") or {}).get("data") or [None])[0])
            if not encoded:
                self._stats["decode_fail"] += 1
                continue
            decoded = self._decode_pool_account(encoded)
            if not decoded:
                self._stats["decode_fail"] += 1
                continue
            decoded["pair_address"] = pubkey
            self._seen_pool_accounts.add(pubkey)
            with self._lock:
                self._pending.append(decoded)
            self._stats["new_pools"] += 1

    def _decode_pool_account(self, encoded: str) -> Optional[dict]:
        raw = base64.b64decode(encoded)
        if len(raw) < self.LIQUIDITY_STATE_V4_SIZE:
            return None
        try:
            status = struct.unpack_from("<Q", raw, self.OFFSET_STATUS)[0]
            if status != 6:
                self._stats["bad_status"] += 1
                return None
            quote_mint = self._b58encode(raw[self.OFFSET_QUOTE_MINT:self.OFFSET_QUOTE_MINT + 32])
            if quote_mint != self.quote_mint:
                self._stats["wrong_quote_mint"] += 1
                return None
            market_program = self._b58encode(raw[self.OFFSET_MARKET_PROGRAM_ID:self.OFFSET_MARKET_PROGRAM_ID + 32])
            if market_program != OPENBOOK_MARKET:
                self._stats["wrong_market_program"] += 1
                return None
            base_mint = self._b58encode(raw[self.OFFSET_BASE_MINT:self.OFFSET_BASE_MINT + 32])
            pool_open_time = struct.unpack_from("<Q", raw, self.OFFSET_POOL_OPEN_TIME)[0]
            return {
                "token_address": base_mint,
                "quote_mint": quote_mint,
                "pool_open_time": pool_open_time,
                "pool_source": "raydium_program_accounts",
            }
        except Exception:
            return None

    def _rpc(self, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.rpc_http_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        if parsed.get("error"):
            raise RuntimeError(f"RPC error: {parsed['error']}")
        return parsed

    @staticmethod
    def _b58encode(data: bytes) -> str:
        if not data:
            return ""
        num = int.from_bytes(data, "big")
        out = ""
        while num > 0:
            num, rem = divmod(num, 58)
            out = BASE58_ALPHABET[rem] + out
        pad = 0
        for b in data:
            if b == 0:
                pad += 1
            else:
                break
        return (BASE58_ALPHABET[0] * pad) + (out or "")

    @staticmethod
    def _encode_u64_le_base58(value: int) -> str:
        return SolanaPoolDiscovery._b58encode(struct.pack("<Q", value))
