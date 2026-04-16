from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Position:
    token_address: str
    pair_address: str
    symbol: str
    name: str
    entry_price_usd: float
    amount_usdc: float
    take_profit_pct: float
    stop_loss_pct: float
    trailing_stop_pct: float
    highest_price_usd: float
    opened_at_ms: int
    last_seen_at_ms: int
    status: str = "open"
    last_price_usd: Optional[float] = None
    tp_armed: bool = False
    break_even_armed: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class ClosedTrade:
    token_address: str
    pair_address: str
    symbol: str
    name: str
    entry_price_usd: float
    exit_price_usd: float
    amount_usdc: float
    pnl_usdc: float
    pnl_pct: float
    exit_reason: str
    opened_at_ms: int
    closed_at_ms: int

    def to_dict(self):
        return asdict(self)
