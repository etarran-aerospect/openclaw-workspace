from dataclasses import dataclass, asdict


@dataclass
class Position:
    market_id: str
    question: str
    side: str
    entry_price: float
    amount_usdc: float
    opened_at: str
    last_price: float
    last_seen_at: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ClosedTrade:
    market_id: str
    question: str
    side: str
    entry_price: float
    exit_price: float
    amount_usdc: float
    pnl_usdc: float
    pnl_pct: float
    reason: str
    opened_at: str
    closed_at: str

    def to_dict(self):
        return asdict(self)
