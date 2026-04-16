import json
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from models.state import ClosedTrade, Position
from services.polymarket import PolymarketGammaClient


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
POSITIONS_PATH = DATA_DIR / "positions.json"
TRADES_PATH = DATA_DIR / "trades.json"
PNL_PATH = DATA_DIR / "pnl_summary.json"
SEEN_PATH = DATA_DIR / "seen_markets.json"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def seconds_since(iso_ts: str) -> float:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return 0


def load_config():
    with open(BASE / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def parse_outcome_prices(market):
    raw = market.get("outcomePrices")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return []
    return [parse_float(x) for x in (raw or [])]


def market_minutes_to_end(market):
    end_date = market.get("endDate")
    if not end_date:
        return None
    try:
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        return (end_dt - datetime.now(timezone.utc)).total_seconds() / 60
    except Exception:
        return None


def normalize_market(market):
    prices = parse_outcome_prices(market)
    yes_price = prices[0] if len(prices) > 0 else None
    no_price = prices[1] if len(prices) > 1 else None
    events = market.get("events") or []
    event = events[0] if events else {}
    category_text = " ".join(
        filter(None, [
            str(event.get("title", "")),
            str(event.get("ticker", "")),
            str(market.get("question", "")),
        ])
    ).lower()
    series_slug = market.get("seriesSlug") or ""
    if not series_slug:
        series = market.get("series") or []
        if series:
            series_slug = series[0].get("slug") or ""
    return {
        "market_id": str(market.get("id")),
        "question": market.get("question", ""),
        "liquidity": parse_float(market.get("liquidity")),
        "volume24hr": parse_float(market.get("volume24hr")),
        "best_bid": parse_float(market.get("bestBid")),
        "best_ask": parse_float(market.get("bestAsk")),
        "last_trade_price": parse_float(market.get("lastTradePrice")),
        "yes_price": yes_price,
        "no_price": no_price,
        "spread": parse_float(market.get("spread")),
        "minutes_to_end": market_minutes_to_end(market),
        "question_text": market.get("question", ""),
        "event_title": event.get("title", ""),
        "event_ticker": event.get("ticker", ""),
        "category_text": category_text,
        "series_slug": series_slug,
    }


def discover_markets(client, config, seen_markets):
    candidates = []
    sample_accept = None
    stats = {
        "total": 0,
        "seen": 0,
        "fetch_fail": 0,
        "liq": 0,
        "vol": 0,
        "near_end": 0,
        "bad_price": 0,
        "accepted": 0,
    }
    target_assets = config["market"].get("target_assets", [])
    now_bucket = int(time.time() // 300 * 300)

    for asset in target_assets:
        slug = f"{asset}-updown-5m-{now_bucket}"
        stats["total"] += 1
        try:
            events = client.event_by_slug(slug)
        except Exception:
            stats["fetch_fail"] += 1
            continue
        if not events:
            stats["fetch_fail"] += 1
            continue
        event = events[0]
        markets = event.get("markets") or []
        if not markets:
            stats["fetch_fail"] += 1
            continue
        market = markets[0]
        mid = str(market.get("id"))
        if mid in seen_markets:
            stats["seen"] += 1
            continue

        merged = dict(market)
        merged["events"] = [event]
        merged["seriesSlug"] = event.get("seriesSlug") or ""
        m = normalize_market(merged)

        if m["liquidity"] < config["market"]["min_liquidity"]:
            stats["liq"] += 1
            continue
        if m["volume24hr"] < config["market"]["min_volume"]:
            stats["vol"] += 1
            continue
        if m["minutes_to_end"] is not None and m["minutes_to_end"] < config["market"]["avoid_near_resolution_minutes"]:
            stats["near_end"] += 1
            continue
        if m["yes_price"] is None or m["yes_price"] <= 0 or m["yes_price"] >= 1:
            stats["bad_price"] += 1
            continue

        candidates.append(m)
        stats["accepted"] += 1
        if sample_accept is None:
            sample_accept = m

    return candidates, stats, sample_accept, [], [], []


def choose_entry_side(market, config):
    edge = config["strategy"]["entry_edge_pct"] / 100
    min_entry = config["strategy"].get("min_entry_price", 0.08)
    max_entry = config["strategy"].get("max_entry_price", 0.45)
    max_spread = config["strategy"].get("require_spread_below", 0.10)

    yes_price = market["yes_price"]
    no_price = market["no_price"]
    spread = market.get("spread", 0)

    if spread and spread > max_spread:
        return None, None

    candidates = []
    if yes_price is not None and min_entry <= yes_price <= max_entry and yes_price < (0.5 - edge):
        candidates.append(("YES", yes_price, 0.5 - yes_price))
    if no_price is not None and min_entry <= no_price <= max_entry and no_price < (0.5 - edge):
        candidates.append(("NO", no_price, 0.5 - no_price))

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0][0], candidates[0][1]


def open_position(market, side, entry_price, config):
    ts = now_iso()
    return Position(
        market_id=market["market_id"],
        question=market["question"],
        side=side,
        entry_price=entry_price,
        amount_usdc=config["portfolio"]["max_position_usdc"],
        opened_at=ts,
        last_price=entry_price,
        last_seen_at=ts,
    )


def market_price_for_side(market, side):
    return market["yes_price"] if side == "YES" else market["no_price"]


def close_trade(pos, exit_price, reason):
    pnl_pct = ((exit_price - pos.entry_price) / pos.entry_price) * 100
    pnl_usdc = pos.amount_usdc * (pnl_pct / 100)
    return ClosedTrade(
        market_id=pos.market_id,
        question=pos.question,
        side=pos.side,
        entry_price=pos.entry_price,
        exit_price=exit_price,
        amount_usdc=pos.amount_usdc,
        pnl_usdc=pnl_usdc,
        pnl_pct=pnl_pct,
        reason=reason,
        opened_at=pos.opened_at,
        closed_at=now_iso(),
    )


def summarize_pnl(trades):
    total = sum(t["pnl_usdc"] for t in trades)
    wins = sum(1 for t in trades if t["pnl_usdc"] > 0)
    losses = sum(1 for t in trades if t["pnl_usdc"] <= 0)
    return {
        "total_pnl_usdc": total,
        "trade_count": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate_pct": (wins / len(trades) * 100) if trades else 0,
        "updated_at": now_iso(),
    }


def print_closed_trade(trade_dict):
    print("-" * 42)
    print("✅ CLOSED TRADE")
    print(f"{trade_dict['side']} | reason={trade_dict['reason']}")
    print(trade_dict['question'][:110])
    print(f"Entry: ${trade_dict['entry_price']:.3f}")
    print(f"Exit:  ${trade_dict['exit_price']:.3f}")
    print(f"PnL:   ${trade_dict['pnl_usdc']:.2f} ({trade_dict['pnl_pct']:+.2f}%)")
    print("-" * 42)


def print_pnl_summary(summary):
    print("=" * 42)
    print("📊 PNL STATUS")
    print("=" * 42)
    print(f"Total PnL: ${summary['total_pnl_usdc']:.2f}")
    print(f"Trades: {summary['trade_count']}")
    print(f"Wins: {summary['wins']} | Losses: {summary['losses']}")
    print(f"Win Rate: {summary['win_rate_pct']:.2f}%")
    print("=" * 42)


def monitor_positions(client, positions, config, closed_trades):
    raw = client.active_markets(limit=200, offset=0)
    market_map = {str(m.get("id")): normalize_market(m) for m in raw}
    still_open = []
    for pos in positions:
        market = market_map.get(pos.market_id)
        if not market:
            if seconds_since(pos.last_seen_at) > config["strategy"]["stale_after_seconds"]:
                trade = close_trade(pos, pos.last_price, "stale_market")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print(f"⌛ CLOSE STALE: {pos.question[:70]}...")
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue
            still_open.append(pos)
            continue
        current_price = market_price_for_side(market, pos.side)
        if current_price is None:
            if seconds_since(pos.last_seen_at) > config["strategy"]["stale_after_seconds"]:
                trade = close_trade(pos, pos.last_price, "stale_price")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print(f"⌛ CLOSE STALE: {pos.question[:70]}...")
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue
            still_open.append(pos)
            continue
        pos.last_price = current_price
        pos.last_seen_at = now_iso()
        pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
        print(f"📈 {pos.side} {pos.question[:70]}... @ {current_price:.3f} ({pnl_pct:+.2f}%)")
        if pnl_pct >= config["strategy"]["exit_take_profit_pct"]:
            trade = close_trade(pos, current_price, "take_profit")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print(f"✅ CLOSE TP: {pos.question[:70]}...")
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue
        if pnl_pct <= -config["strategy"]["exit_stop_loss_pct"]:
            trade = close_trade(pos, current_price, "stop_loss")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print(f"🛑 CLOSE SL: {pos.question[:70]}...")
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue
        still_open.append(pos)
    return still_open, closed_trades


def hydrate_position(raw):
    ts = now_iso()
    raw.setdefault("last_seen_at", raw.get("opened_at", ts))
    return Position(**raw)


def main():
    config = load_config()
    client = PolymarketGammaClient()
    positions = [hydrate_position(p) for p in load_json(POSITIONS_PATH, [])]
    closed_trades = load_json(TRADES_PATH, [])
    seen_markets = set(load_json(SEEN_PATH, []))

    print("Prediction Bot V1 starting")
    print("=" * 42)
    print("⚙️ STARTUP SETTINGS")
    print("=" * 42)
    print("MARKET")
    for k, v in config["market"].items():
        print(f"- {k}: {v}")
    print("PORTFOLIO")
    for k, v in config["portfolio"].items():
        print(f"- {k}: {v}")
    print("STRATEGY")
    for k, v in config["strategy"].items():
        print(f"- {k}: {v}")
    print("MONITOR")
    for k, v in config["monitor"].items():
        print(f"- {k}: {v}")
    print("=" * 42)

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] cycle start, open_positions={len(positions)}")
        if len(positions) < config["portfolio"]["max_open_positions"]:
            candidates, stats, sample_accept, sample_allow_miss, sample_block_hit, sample_pattern_miss = discover_markets(client, config, seen_markets)
            print("discovery:", stats)
            if sample_accept:
                print(
                    "sample accepted:",
                    sample_accept["question"][:90],
                    f"| yes={sample_accept['yes_price']}",
                    f"| no={sample_accept['no_price']}",
                    f"| liq={sample_accept['liquidity']:.0f}",
                    f"| vol24h={sample_accept['volume24hr']:.0f}",
                    f"| mins_to_end={sample_accept['minutes_to_end']:.1f}" if sample_accept['minutes_to_end'] is not None else "| mins_to_end=n/a"
                )
            if sample_allow_miss:
                print("sample allow_miss:")
                for q in sample_allow_miss:
                    print("-", q[:110])
            if sample_block_hit:
                print("sample block_hit:")
                for q in sample_block_hit:
                    print("-", q[:110])
            if sample_pattern_miss:
                print("sample pattern_miss:")
                for q, s in sample_pattern_miss:
                    print("-", q[:95], f"| series={s or 'n/a'}")
            if not candidates:
                print("no markets passed filters this cycle")

            entry_rejections = {"edge_or_price": 0, "capacity": 0}
            opened_this_cycle = 0
            for market in candidates:
                if len(positions) >= config["portfolio"]["max_open_positions"]:
                    entry_rejections["capacity"] += 1
                    break
                side, entry_price = choose_entry_side(market, config)
                if side is None:
                    entry_rejections["edge_or_price"] += 1
                    continue
                pos = open_position(market, side, entry_price, config)
                positions.append(pos)
                seen_markets.add(market["market_id"])
                opened_this_cycle += 1
                print("-" * 42)
                print("📝 PAPER OPEN")
                print(f"Side: {side}")
                print(f"Entry: ${entry_price:.3f}")
                print(f"Question: {market['question'][:120]}")
                print(f"Liquidity: ${market['liquidity']:.0f} | Volume24h: ${market['volume24hr']:.0f} | Spread: {market['spread']:.3f}")
                print("-" * 42)
            print(f"entry summary: opened={opened_this_cycle} rejected_edge_or_price={entry_rejections['edge_or_price']} capacity_blocked={entry_rejections['capacity']}")
        positions, closed_trades = monitor_positions(client, positions, config, closed_trades)
        save_json(POSITIONS_PATH, [p.to_dict() for p in positions])
        save_json(TRADES_PATH, closed_trades)
        save_json(SEEN_PATH, sorted(seen_markets))
        save_json(PNL_PATH, summarize_pnl(closed_trades))
        time.sleep(config["monitor"]["poll_interval_seconds"])


if __name__ == "__main__":
    main()
