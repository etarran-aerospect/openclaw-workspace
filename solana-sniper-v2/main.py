import json
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from models.state import ClosedTrade, Position
from services.dexscreener import DexScreenerClient
from services.gmgn_discovery import GmgnDiscovery
from services.solana_discovery import SolanaPoolDiscovery, USDC_MINT, WSOL_MINT


BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
POSITIONS_PATH = DATA_DIR / "positions.json"
TRADES_PATH = DATA_DIR / "trades.json"
SEEN_PATH = DATA_DIR / "seen_tokens.json"
PNL_PATH = DATA_DIR / "pnl_summary.json"

PRESETS = {
    "wallet_copy_early": {
        "filters": {
            "min_liquidity_usd": 250,
            "max_entry_move_pct": 25,
        },
        "gmgn_filters": {
            "max_open_minutes": 45,
            "max_rug_ratio": 0.4,
            "max_bundler_rate": 0.5,
            "max_top_10_holder_rate": 0.5,
            "require_socials": False,
            "allow_creator_hold": True,
        },
        "pre_migration_filters": {
            "enabled": True,
            "allowed_buckets": ["new_creation", "near_completion"],
            "min_market_cap_usd": 2500,
            "max_market_cap_usd": 15000,
            "min_liquidity_usd": 300,
            "min_holder_count": 10,
            "min_progress_pct": 0,
            "max_progress_pct": 95,
            "max_rug_ratio": 0.4,
            "max_bundler_rate": 0.5,
            "require_socials": False,
        },
        "monitor": {
            "exit_if_liquidity_below_usd": 800,
            "exit_if_volume_5m_below_usd": 25,
            "exit_if_buys_5m_below": 1,
            "post_migration_fail_if_pnl_below_pct": -10,
            "post_migration_fail_if_liquidity_below_usd": 1000,
            "post_migration_fail_if_volume_5m_below_usd": 25,
            "post_migration_fail_if_buys_5m_below": 1,
        },
        "ladder": {
            "probe_buy_usdc": 20,
            "probe_buy_count": 3,
            "probe_spacing_seconds": 5,
            "confirm_buy_usdc": 250,
            "confirm_min_liquidity_usd": 300,
            "confirm_min_volume_5m_usd": 25,
            "confirm_min_buys_5m": 1,
            "confirm_max_drawdown_pct": 12,
            "require_price_above_probe_avg": False,
            "require_liquidity_not_falling": False,
        },
    },
    "aggressive": {
        "filters": {
            "min_liquidity_usd": 250,
            "max_entry_move_pct": 20,
        },
        "gmgn_filters": {
            "max_open_minutes": 90,
            "max_rug_ratio": 0.4,
            "max_bundler_rate": 0.45,
            "max_top_10_holder_rate": 0.55,
            "require_socials": False,
            "allow_creator_hold": True,
        },
        "pre_migration_filters": {
            "enabled": True,
            "allowed_buckets": ["new_creation", "near_completion"],
            "min_market_cap_usd": 750,
            "max_market_cap_usd": 70000,
            "min_liquidity_usd": 2000,
            "min_holder_count": 5,
            "min_progress_pct": 0.15,
            "max_progress_pct": 98,
            "max_rug_ratio": 0.35,
            "max_bundler_rate": 0.45,
            "require_socials": False,
        },
        "monitor": {
            "exit_if_liquidity_below_usd": 1000,
            "exit_if_volume_5m_below_usd": 50,
            "exit_if_buys_5m_below": 1,
        },
        "ladder": {
            "probe_buy_usdc": 20,
            "probe_buy_count": 4,
            "probe_spacing_seconds": 6,
            "confirm_buy_usdc": 250,
            "confirm_min_liquidity_usd": 2500,
            "confirm_min_volume_5m_usd": 75,
            "confirm_min_buys_5m": 2,
            "confirm_max_drawdown_pct": 10,
            "require_price_above_probe_avg": False,
            "require_liquidity_not_falling": False,
        },
    },
    "balanced": {
        "filters": {
            "min_liquidity_usd": 500,
            "max_entry_move_pct": 15,
        },
        "gmgn_filters": {
            "max_open_minutes": 45,
            "max_rug_ratio": 0.3,
            "max_bundler_rate": 0.45,
            "max_top_10_holder_rate": 0.55,
            "require_socials": False,
            "allow_creator_hold": True,
        },
        "pre_migration_filters": {
            "enabled": True,
            "allowed_buckets": ["new_creation", "near_completion"],
            "min_market_cap_usd": 750,
            "max_market_cap_usd": 70000,
            "min_liquidity_usd": 1500,
            "min_holder_count": 5,
            "min_progress_pct": 0.15,
            "max_progress_pct": 98,
            "max_rug_ratio": 0.25,
            "max_bundler_rate": 0.25,
            "require_socials": False,
        },
        "post_migration_launch_filters": {
            "enabled": True,
            "allowed_buckets": ["completed"],
            "min_market_cap_usd": 10000,
            "max_market_cap_usd": 750000,
            "min_liquidity_usd": 10000,
            "min_volume_5m_usd": 2500,
            "min_buys_5m": 5,
            "max_rug_ratio": 0.3,
            "max_bundler_rate": 0.35,
            "max_age_minutes": 30,
        },
        "monitor": {
            "exit_if_liquidity_below_usd": 2000,
            "exit_if_volume_5m_below_usd": 100,
            "exit_if_buys_5m_below": 2,
            "post_migration_grace_period_seconds": 25,
            "discovery_interval_seconds": 20,
            "price_poll_interval_seconds": 5,
            "stale_after_seconds": 90,
        },
        "ladder": {
            "probe_buy_usdc": 20,
            "probe_buy_count": 3,
            "probe_spacing_seconds": 8,
            "confirm_buy_usdc": 100,
            "confirm_min_liquidity_usd": 3000,
            "confirm_min_volume_5m_usd": 75,
            "confirm_min_buys_5m": 2,
            "confirm_max_drawdown_pct": 8,
            "require_price_above_probe_avg": False,
            "require_liquidity_not_falling": True,
        },
    },
    "conservative": {
        "filters": {
            "min_liquidity_usd": 1000,
            "max_entry_move_pct": 10,
        },
        "gmgn_filters": {
            "max_open_minutes": 25,
            "max_rug_ratio": 0.2,
            "max_bundler_rate": 0.25,
            "max_top_10_holder_rate": 0.25,
            "require_socials": True,
            "allow_creator_hold": False,
        },
        "pre_migration_filters": {
            "enabled": True,
            "allowed_buckets": ["new_creation", "near_completion"],
            "min_market_cap_usd": 4000,
            "max_market_cap_usd": 20000,
            "min_liquidity_usd": 5000,
            "min_holder_count": 75,
            "min_progress_pct": 70,
            "max_progress_pct": 95,
            "max_rug_ratio": 0.2,
            "max_bundler_rate": 0.2,
            "require_socials": True,
        },
        "monitor": {
            "exit_if_liquidity_below_usd": 5000,
            "exit_if_volume_5m_below_usd": 250,
            "exit_if_buys_5m_below": 3,
        },
        "ladder": {
            "probe_buy_usdc": 15,
            "probe_buy_count": 3,
            "probe_spacing_seconds": 10,
            "confirm_buy_usdc": 75,
            "confirm_min_liquidity_usd": 5000,
            "confirm_min_volume_5m_usd": 150,
            "confirm_min_buys_5m": 3,
            "confirm_max_drawdown_pct": 6,
            "require_price_above_probe_avg": True,
            "require_liquidity_not_falling": True,
        },
    },
}


def now_ms() -> int:
    return int(time.time() * 1000)


def _deep_update(base: dict, overrides: dict):
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def load_config():
    with open(BASE / "config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    preset_name = config.get("preset", "balanced")
    preset_values = PRESETS.get(preset_name)
    if preset_values is None:
        raise ValueError(f"Unknown preset: {preset_name}. Valid presets: {', '.join(sorted(PRESETS))}")
    merged = {
        "preset": preset_name,
        "portfolio": {},
        "filters": {},
        "gmgn_filters": {},
        "pre_migration_filters": {},
        "trade": {},
        "ladder": {},
        "monitor": {},
        "discovery": {},
    }
    _deep_update(merged, preset_values)
    _deep_update(merged, config)
    return merged


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def pair_age_minutes(pair):
    created = pair.get("pairCreatedAt")
    if not created:
        return None
    return max(0, (now_ms() - int(created)) / 60000)


def has_socials(pair):
    info = pair.get("info") or {}
    socials = info.get("socials") or []
    websites = info.get("websites") or []
    return bool(socials or websites)


def is_blacklisted(candidate, config):
    terms = [t.lower() for t in config["filters"].get("blacklist_terms", [])]
    hay = f"{candidate['symbol']} {candidate['name']}".lower()
    return any(term in hay for term in terms)


def normalize_candidate(profile, pair):
    return {
        "token_address": profile["tokenAddress"],
        "symbol": pair["baseToken"]["symbol"],
        "name": pair["baseToken"]["name"],
        "pair_address": pair["pairAddress"],
        "price_usd": float(pair.get("priceUsd") or 0),
        "liquidity_usd": float((pair.get("liquidity") or {}).get("usd") or 0),
        "volume_m5": float((pair.get("volume") or {}).get("m5") or 0),
        "buys_m5": int((((pair.get("txns") or {}).get("m5") or {}).get("buys") or 0)),
        "fdv_usd": float(pair.get("fdv") or 0),
        "quote_symbol": ((pair.get("quoteToken") or {}).get("symbol") or ""),
        "pair_age_minutes": pair_age_minutes(pair),
        "has_socials": has_socials(pair),
    }


def _empty_discovery_stats(source_name: str):
    return {
        "source": source_name,
        "profiles": 0,
        "onchain_candidates": 0,
        "non_solana": 0,
        "seen": 0,
        "pair_fetch_fail": 0,
        "bad_price": 0,
        "age": 0,
        "liquidity": 0,
        "volume": 0,
        "buys": 0,
        "quote": 0,
        "fdv": 0,
        "socials": 0,
        "blacklist": 0,
        "gmgn_launchpad": 0,
        "gmgn_rug": 0,
        "gmgn_bundler": 0,
        "gmgn_holders": 0,
        "gmgn_top10": 0,
        "gmgn_smart": 0,
        "gmgn_renowned": 0,
        "gmgn_owner": 0,
        "gmgn_creator": 0,
        "gmgn_open_age": 0,
        "gmgn_raw_empty": 0,
        "gmgn_prefilter_pass": 0,
        "gmgn_prefilter_reject": 0,
        "pm_bucket": 0,
        "pm_mc": 0,
        "pm_liq": 0,
        "pm_holders": 0,
        "pm_progress": 0,
        "pm_rug": 0,
        "pm_bundler": 0,
        "pm_socials": 0,
        "pm_mc_examples": [],
        "pm_liq_examples": [],
        "raw_examples": [],
        "entry_move": 0,
        "accepted": 0,
    }


def _gmgn_prefilter(raw, config, stats):
    gmgn_cfg = config.get("gmgn_filters", {})
    if not gmgn_cfg.get("enabled", False):
        return True

    allowed = set(gmgn_cfg.get("allowed_launchpad_platforms") or [])
    if allowed and raw.get("launchpad_platform") not in allowed:
        stats["gmgn_launchpad"] += 1
        return False
    open_ts = int(raw.get("open_timestamp") or 0)
    max_open_minutes = gmgn_cfg.get("max_open_minutes")
    if max_open_minutes is not None and open_ts > 0:
        open_age_minutes = max(0, (int(time.time()) - open_ts) / 60)
        if open_age_minutes > max_open_minutes:
            stats["gmgn_open_age"] += 1
            return False
    if raw.get("rug_ratio", 0) > gmgn_cfg.get("max_rug_ratio", 1):
        stats["gmgn_rug"] += 1
        return False
    if raw.get("bundler_rate", 0) > gmgn_cfg.get("max_bundler_rate", 1):
        stats["gmgn_bundler"] += 1
        return False
    if raw.get("holder_count", 0) < gmgn_cfg.get("min_holder_count", 0):
        stats["gmgn_holders"] += 1
        return False
    if raw.get("top_10_holder_rate", 0) > gmgn_cfg.get("max_top_10_holder_rate", 1):
        stats["gmgn_top10"] += 1
        return False
    if raw.get("smart_degen_count", 0) < gmgn_cfg.get("min_smart_degen_count", 0):
        stats["gmgn_smart"] += 1
        return False
    if raw.get("renowned_count", 0) < gmgn_cfg.get("min_renowned_count", 0):
        stats["gmgn_renowned"] += 1
        return False
    if gmgn_cfg.get("require_owner_renounced", False) and not raw.get("owner_renounced", False):
        stats["gmgn_owner"] += 1
        return False
    if gmgn_cfg.get("require_socials", False) and not raw.get("has_socials", False):
        stats["socials"] += 1
        return False
    if not gmgn_cfg.get("allow_creator_hold", True) and raw.get("creator_token_status") == "creator_hold":
        stats["gmgn_creator"] += 1
        return False
    return True


def _append_example(stats, key, value, limit=3):
    values = stats.setdefault(key, [])
    if len(values) < limit:
        values.append(value)


def _pre_migration_prefilter(raw, config, stats):
    pm_cfg = config.get("pre_migration_filters", {})
    if not pm_cfg.get("enabled", False):
        return True
    allowed_buckets = set(pm_cfg.get("allowed_buckets") or [])
    if allowed_buckets and raw.get("gmgn_bucket") not in allowed_buckets:
        stats["pm_bucket"] += 1
        return False
    fdv_usd = float(raw.get("fdv_usd") or 0)
    if fdv_usd < pm_cfg.get("min_market_cap_usd", 0) or fdv_usd > pm_cfg.get("max_market_cap_usd", float("inf")):
        stats["pm_mc"] += 1
        _append_example(stats, "pm_mc_examples", f"{raw.get('symbol') or raw.get('token_address')[:8]}:{raw.get('gmgn_bucket')}:${fdv_usd:.0f}")
        return False
    liquidity_usd = float(raw.get("liquidity_usd") or 0)
    if liquidity_usd < pm_cfg.get("min_liquidity_usd", 0):
        stats["pm_liq"] += 1
        _append_example(stats, "pm_liq_examples", f"{raw.get('symbol') or raw.get('token_address')[:8]}:{raw.get('gmgn_bucket')}:${liquidity_usd:.0f}")
        return False
    if int(raw.get("holder_count") or 0) < pm_cfg.get("min_holder_count", 0):
        stats["pm_holders"] += 1
        return False
    progress_pct = float(raw.get("progress_pct") or 0)
    if progress_pct < pm_cfg.get("min_progress_pct", 0) or progress_pct > pm_cfg.get("max_progress_pct", 100):
        stats["pm_progress"] += 1
        return False
    if float(raw.get("rug_ratio") or 0) > pm_cfg.get("max_rug_ratio", 1):
        stats["pm_rug"] += 1
        return False
    if float(raw.get("bundler_rate") or 0) > pm_cfg.get("max_bundler_rate", 1):
        stats["pm_bundler"] += 1
        return False
    if pm_cfg.get("require_socials", False) and not raw.get("has_socials", False):
        stats["pm_socials"] += 1
        return False
    return True


def _post_migration_launch_prefilter(raw, config, stats):
    pml_cfg = config.get("post_migration_launch_filters", {})
    if not pml_cfg.get("enabled", False):
        return True
    allowed_buckets = set(pml_cfg.get("allowed_buckets") or [])
    if allowed_buckets and raw.get("gmgn_bucket") not in allowed_buckets:
        return False
    
    fdv_usd = float(raw.get("fdv_usd") or 0)
    if fdv_usd < pml_cfg.get("min_market_cap_usd", 0) or fdv_usd > pml_cfg.get("max_market_cap_usd", float("inf")):
        _append_example(stats, "pm_mc_examples", f"POST:{raw.get('symbol') or raw.get('token_address')[:8]}:${fdv_usd:.0f}")
        return False
        
    liquidity_usd = float(raw.get("liquidity_usd") or 0)
    if liquidity_usd < pml_cfg.get("min_liquidity_usd", 0):
        _append_example(stats, "pm_liq_examples", f"POST:{raw.get('symbol') or raw.get('token_address')[:8]}:${liquidity_usd:.0f}")
        return False

    # Check age if restricted
    max_age = pml_cfg.get("max_age_minutes")
    if max_age is not None:
        open_ts = int(raw.get("open_timestamp") or 0)
        if open_ts > 0:
            age_min = (int(time.time()) - open_ts) / 60
            if age_min > max_age:
                return False

    if float(raw.get("rug_ratio") or 0) > pml_cfg.get("max_rug_ratio", 1):
        return False
        
    if float(raw.get("bundler_rate") or 0) > pml_cfg.get("max_bundler_rate", 1):
        return False

    return True


def _candidate_from_token(client, token, config, seen_tokens, stats, raw_hint=None, strategy_mode=None):
    if token in seen_tokens:
        stats["seen"] += 1
        return None
    try:
        pairs = client.token_pairs(token)
    except Exception:
        stats["pair_fetch_fail"] += 1
        return None
    for pair in pairs:
        if pair.get("chainId") != "solana":
            continue
        if float(pair.get("priceUsd") or 0) <= 0:
            stats["bad_price"] += 1
            continue
        profile = {
            "tokenAddress": token,
        }
        candidate = normalize_candidate(profile, pair)
        if raw_hint is not None:
            candidate["gmgn_raw"] = raw_hint.get("gmgn_raw")
            candidate["launchpad_platform"] = raw_hint.get("launchpad_platform")
            candidate["gmgn_bucket"] = raw_hint.get("gmgn_bucket")
            candidate["progress_pct"] = raw_hint.get("progress_pct")
            candidate["rug_ratio"] = raw_hint.get("rug_ratio")
            candidate["bundler_rate"] = raw_hint.get("bundler_rate")
            candidate["top_10_holder_rate"] = raw_hint.get("top_10_holder_rate")
            candidate["smart_degen_count"] = raw_hint.get("smart_degen_count")
            candidate["renowned_count"] = raw_hint.get("renowned_count")
            candidate["holder_count"] = raw_hint.get("holder_count")
            candidate["owner_renounced"] = raw_hint.get("owner_renounced")
            candidate["creator_token_status"] = raw_hint.get("creator_token_status")
            candidate["gmgn_liquidity_usd"] = raw_hint.get("liquidity_usd")
            candidate["gmgn_fdv_usd"] = raw_hint.get("fdv_usd")
            candidate["gmgn_created_timestamp"] = raw_hint.get("created_timestamp")
            candidate["gmgn_open_timestamp"] = raw_hint.get("open_timestamp")
            gmgn_fdv = float(raw_hint.get("fdv_usd") or 0)
            if gmgn_fdv > 0 and candidate["fdv_usd"] > 0:
                entry_move_pct = abs(candidate["fdv_usd"] - gmgn_fdv) / gmgn_fdv * 100
                candidate["entry_move_pct"] = entry_move_pct
                if strategy_mode != "pre_migration_ladder" and entry_move_pct > config["filters"].get("max_entry_move_pct", 1000):
                    stats["entry_move"] += 1
                    continue
        age = candidate["pair_age_minutes"]
        if strategy_mode != "pre_migration_ladder":
            if age is None or age < config["filters"]["min_age_minutes"] or age > config["filters"]["max_age_minutes"]:
                stats["age"] += 1
                continue
        if strategy_mode != "pre_migration_ladder" and candidate["liquidity_usd"] < config["filters"]["min_liquidity_usd"]:
            stats["liquidity"] += 1
            continue
        if candidate["volume_m5"] < config["filters"]["min_volume_5m_usd"]:
            stats["volume"] += 1
            continue
        if candidate["buys_m5"] < config["filters"]["min_buys_5m"]:
            stats["buys"] += 1
            continue
        if candidate["quote_symbol"] != config["filters"]["require_quote_symbol"]:
            stats["quote"] += 1
            continue
        if candidate["fdv_usd"] < config["filters"]["min_fdv_usd"] or candidate["fdv_usd"] > config["filters"]["max_fdv_usd"]:
            stats["fdv"] += 1
            continue
        if config["filters"].get("block_missing_socials") and not candidate["has_socials"]:
            stats["socials"] += 1
            continue
        if is_blacklisted(candidate, config):
            stats["blacklist"] += 1
            continue
        stats["accepted"] += 1
        return candidate
    return None


def discover_candidates(client, config, seen_tokens, onchain_discovery=None, gmgn_discovery=None):
    source = config.get("discovery", {}).get("source", "dexscreener")
    stats = _empty_discovery_stats(source)
    out = []
    strategy_mode = config.get("strategy_mode", "single_buy")

    if source == "gmgn" and gmgn_discovery is not None:
        raw_candidates = gmgn_discovery.pop_pending_candidates()
        if strategy_mode == "pre_migration_ladder":
            raw_candidates.sort(key=lambda x: (x.get("gmgn_bucket") == "near_completion", float(x.get("progress_pct") or 0), int(x.get("created_timestamp") or 0)), reverse=True)
        else:
            raw_candidates.sort(key=lambda x: int(x.get("open_timestamp") or 0), reverse=True)
        stats["onchain_candidates"] = len(raw_candidates)
        if not raw_candidates:
            stats["gmgn_raw_empty"] += 1
        for raw in raw_candidates:
            bucket = raw.get("gmgn_bucket")
            _append_example(
                stats,
                "raw_examples",
                f"{raw.get('symbol') or raw.get('token_address')[:8]}:{bucket} progress={float(raw.get('progress_pct') or 0):.1f}% mc=${float(raw.get('fdv_usd') or 0):.0f} liq=${float(raw.get('liquidity_usd') or 0):.0f} holders={int(raw.get('holder_count') or 0)} rug={float(raw.get('rug_ratio') or 0):.2f} bundler={float(raw.get('bundler_rate') or 0):.2f}",
                limit=10 if bucket == "completed" else 5,
            )
            token = raw["token_address"]
            
            # Check Pre-Migration Path
            pre_ok = _pre_migration_prefilter(raw, config, stats) if strategy_mode == "pre_migration_ladder" else _gmgn_prefilter(raw, config, stats)
            
            # Check Post-Migration Path (Secondary)
            post_ok = _post_migration_launch_prefilter(raw, config, stats) if strategy_mode == "pre_migration_ladder" else False
            
            if not pre_ok and not post_ok:
                stats["gmgn_prefilter_reject"] += 1
                continue
            
            stats["gmgn_prefilter_pass"] += 1
            candidate = _candidate_from_token(client, token, config, seen_tokens, stats, raw_hint=raw, strategy_mode=strategy_mode)
            if candidate:
                candidate["discovery_source"] = raw.get("pool_source", "gmgn")
                candidate["gmgn_source_url"] = raw.get("source_url")
                out.append(candidate)
        if out:
            return out, stats

        fallback_enabled = config.get("discovery", {}).get("fallback_to_dexscreener", True)
        gmgn_stats = gmgn_discovery.get_stats()
        has_error = bool(gmgn_stats.get("last_error"))
        empty_polls = gmgn_stats.get("poll_attempts", 0) >= config.get("discovery", {}).get("fallback_after_empty_polls", 2) and gmgn_stats.get("last_result_count", 0) == 0
        if fallback_enabled and (empty_polls or has_error):
            stats["source"] = "gmgn->dexscreener_fallback"
        else:
            return out, stats

    if source == "onchain" and onchain_discovery is not None:
        raw_candidates = onchain_discovery.pop_pending_candidates()
        stats["onchain_candidates"] = len(raw_candidates)
        for raw in raw_candidates:
            token = raw["token_address"]
            candidate = _candidate_from_token(client, token, config, seen_tokens, stats, strategy_mode=strategy_mode)
            if candidate:
                candidate["discovery_source"] = raw.get("pool_source", "onchain")
                candidate["pool_open_time"] = raw.get("pool_open_time")
                out.append(candidate)
        if out:
            return out, stats

        fallback_enabled = config.get("discovery", {}).get("fallback_to_dexscreener", True)
        fallback_after_empty_polls = config.get("discovery", {}).get("fallback_after_empty_polls", 2)
        onchain_stats = onchain_discovery.get_stats()
        has_rpc_error = bool(onchain_stats.get("last_error"))
        empty_polls = onchain_stats.get("poll_attempts", 0) >= fallback_after_empty_polls and onchain_stats.get("last_result_count", 0) == 0
        if fallback_enabled and (empty_polls or has_rpc_error):
            stats["source"] = "onchain->dexscreener_fallback"
        else:
            return out, stats

    profiles = client.latest_token_profiles()
    for profile in profiles:
        stats["profiles"] += 1
        if profile.get("chainId") != "solana":
            stats["non_solana"] += 1
            continue
        candidate = _candidate_from_token(client, profile["tokenAddress"], config, seen_tokens, stats, strategy_mode=strategy_mode)
        if candidate:
            candidate["discovery_source"] = "dexscreener_latest_profiles"
            out.append(candidate)
    return out, stats


def open_position(candidate, config, amount_override=None):
    tp = config["trade"]["take_profit_pct"]
    sl = config["trade"]["stop_loss_pct"]
    trailing = config["trade"]["trailing_stop_pct"]
    amount = amount_override if amount_override is not None else config["trade"]["amount_usdc"]
    ts = now_ms()
    return Position(
        token_address=candidate["token_address"],
        pair_address=candidate["pair_address"],
        symbol=candidate["symbol"],
        name=candidate["name"],
        entry_price_usd=candidate["price_usd"],
        amount_usdc=amount,
        take_profit_pct=tp,
        stop_loss_pct=sl,
        trailing_stop_pct=trailing,
        highest_price_usd=candidate["price_usd"],
        last_price_usd=candidate["price_usd"],
        opened_at_ms=ts,
        last_seen_at_ms=ts,
        tp_armed=False,
        break_even_armed=False,
    )


def close_trade(pos, exit_price, reason):
    pnl_pct = ((exit_price - pos.entry_price_usd) / pos.entry_price_usd) * 100
    pnl_usdc = pos.amount_usdc * (pnl_pct / 100)
    # Ensure PnL calc uses the same logic as the display
    print(f"DEBUG: {pos.symbol} Entry: {pos.entry_price_usd} Exit: {exit_price} PnL%: {pnl_pct}")
    return ClosedTrade(
        token_address=pos.token_address,
        pair_address=pos.pair_address,
        symbol=pos.symbol,
        name=pos.name,
        entry_price_usd=pos.entry_price_usd,
        exit_price_usd=exit_price,
        amount_usdc=pos.amount_usdc,
        pnl_usdc=pnl_usdc,
        pnl_pct=pnl_pct,
        exit_reason=reason,
        opened_at_ms=pos.opened_at_ms,
        closed_at_ms=now_ms(),
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
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def print_pnl_summary(summary):
    print("=" * 42)
    print("📊 PNL STATUS")
    print("=" * 42)
    print(f"Total PnL: ${summary['total_pnl_usdc']:.2f}")
    print(f"Trades: {summary['trade_count']}")
    print(f"Wins: {summary['wins']} | Losses: {summary['losses']}")
    print(f"Win Rate: {summary['win_rate_pct']:.2f}%")
    print("=" * 42)


def print_closed_trade(trade_dict):
    print("-" * 42)
    print("✅ CLOSED TRADE")
    print(f"{trade_dict['symbol']} | reason={trade_dict['exit_reason']} | ca={trade_dict['token_address']} | pair={trade_dict['pair_address']}")
    print(f"Entry: ${trade_dict['entry_price_usd']:.10f}")
    print(f"Exit:  ${trade_dict['exit_price_usd']:.10f}")
    print(f"PnL:   ${trade_dict['pnl_usdc']:.2f} ({trade_dict['pnl_pct']:+.2f}%)")
    print("-" * 42)


def monitor_positions(client, positions, config, closed_trades):
    still_open = []
    stale_after_ms = config["monitor"]["stale_after_seconds"] * 1000

    for pos in positions:
        try:
            pairs = client.token_pairs(pos.token_address)
        except Exception:
            if now_ms() - pos.last_seen_at_ms > stale_after_ms:
                trade = close_trade(pos, pos.last_price_usd or pos.entry_price_usd, "stale_timeout")
                print(f"⌛ SELL {pos.symbol}: stale timeout")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
            else:
                print(f"⌛ {pos.symbol}: price lookup failed")
                still_open.append(pos)
            continue

        match = next((p for p in pairs if p.get("pairAddress") == pos.pair_address), None)
        if not match:
            if now_ms() - pos.last_seen_at_ms > stale_after_ms:
                trade = close_trade(pos, pos.last_price_usd or pos.entry_price_usd, "pair_missing")
                print(f"⌛ SELL {pos.symbol}: pair disappeared")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
            else:
                print(f"⌛ {pos.symbol}: pair not found")
                still_open.append(pos)
            continue

        price = float(match.get("priceUsd") or 0)
        if price <= 0:
            still_open.append(pos)
            continue

        pos.last_seen_at_ms = now_ms()
        pos.last_price_usd = price
        if price > pos.highest_price_usd:
            pos.highest_price_usd = price

        liquidity_usd = float((match.get("liquidity") or {}).get("usd") or 0)
        volume_m5 = float((match.get("volume") or {}).get("m5") or 0)
        buys_m5 = int((((match.get("txns") or {}).get("m5") or {}).get("buys") or 0))
        pnl_pct = ((price - pos.entry_price_usd) / pos.entry_price_usd) * 100
        trailing_stop_price = pos.highest_price_usd * (1 - pos.trailing_stop_pct / 100)
        break_even_price = pos.entry_price_usd
        tp_mode = config["trade"].get("tp_mode", "hybrid")
        break_even_after_tp = config["trade"].get("break_even_after_tp", True)
        min_hold_seconds = config["monitor"].get("min_hold_seconds", 0)
        held_ms = now_ms() - pos.opened_at_ms
        held_long_enough = held_ms >= (min_hold_seconds * 1000)
        post_migration_window_ms = config["monitor"].get("post_migration_acceptance_window_seconds", 0) * 1000
        post_migration_grace_ms = config["monitor"].get("post_migration_grace_period_seconds", 10) * 1000
        in_post_migration_window = held_ms <= post_migration_window_ms if post_migration_window_ms > 0 else False
        in_post_migration_grace = held_ms <= post_migration_grace_ms

        print(
            f"💰 {pos.symbol}: ${price:.10f} ({pnl_pct:+.2f}%)"
            f" | liq=${liquidity_usd:.0f} vol5m=${volume_m5:.0f} buys5m={buys_m5}"
            f" | ca={pos.token_address} pair={pos.pair_address}"
        )

        if tp_mode == "fixed" and pnl_pct >= pos.take_profit_pct:
            trade = close_trade(pos, price, "take_profit")
            print(f"🎯 SELL {pos.symbol}: take profit hit at {pnl_pct:+.2f}%")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue

        if tp_mode == "hybrid" and pnl_pct >= pos.take_profit_pct and not pos.tp_armed:
            pos.tp_armed = True
            if break_even_after_tp:
                pos.break_even_armed = True
            print(f"🎯 {pos.symbol}: TP armed at {pnl_pct:+.2f}%, trailing now active")

        if pos.break_even_armed and price <= break_even_price:
            trade = close_trade(pos, price, "break_even_after_tp")
            print(f"🟡 SELL {pos.symbol}: returned to break-even after TP")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue

        if in_post_migration_window and not in_post_migration_grace:
            weak_liquidity = liquidity_usd < config["monitor"].get("post_migration_fail_if_liquidity_below_usd", 0)
            weak_volume = volume_m5 < config["monitor"].get("post_migration_fail_if_volume_5m_below_usd", 0)
            weak_buys = buys_m5 < config["monitor"].get("post_migration_fail_if_buys_5m_below", 0)
            weakness_count = int(weak_liquidity) + int(weak_volume) + int(weak_buys)

            if pnl_pct <= -config["monitor"].get("post_migration_fail_if_pnl_below_pct", 999):
                # Only reject on PnL during the window if NOT in grace and also seeing at least one weakness signal
                if weakness_count >= 1:
                    trade = close_trade(pos, price, "post_migration_rejection")
                    print(f"🚨 SELL {pos.symbol}: post-migration rejection (PnL {pnl_pct:+.2f}% + weakness)")
                    closed_trade = trade.to_dict()
                    closed_trades.append(closed_trade)
                    print_closed_trade(closed_trade)
                    print_pnl_summary(summarize_pnl(closed_trades))
                    continue
                else:
                    print(f"🛡️ {pos.symbol}: post-migration PnL dip ({pnl_pct:+.2f}%) but volume/liq is strong, holding.")

            if weakness_count >= 2:
                if weak_liquidity and weak_volume:
                    reason = "post_migration_liquidity_volume_fail"
                    msg = f"🚨 SELL {pos.symbol}: post-migration liquidity+volume fail (liq=${liquidity_usd:.0f}, vol5m=${volume_m5:.0f})"
                elif weak_volume and weak_buys:
                    reason = "post_migration_volume_buy_flow_fail"
                    msg = f"🚨 SELL {pos.symbol}: post-migration volume+buy-flow fail (vol5m=${volume_m5:.0f}, buys5m={buys_m5})"
                elif weak_liquidity and weak_buys:
                    reason = "post_migration_liquidity_buy_flow_fail"
                    msg = f"🚨 SELL {pos.symbol}: post-migration liquidity+buy-flow fail (liq=${liquidity_usd:.0f}, buys5m={buys_m5})"
                else:
                    reason = "post_migration_multi_signal_fail"
                    msg = f"🚨 SELL {pos.symbol}: post-migration multi-signal fail"
                trade = close_trade(pos, price, reason)
                print(msg)
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue

        if held_long_enough:
            if liquidity_usd < config["monitor"].get("exit_if_liquidity_below_usd", 0):
                trade = close_trade(pos, price, "liquidity_dried_up")
                print(f"💧 SELL {pos.symbol}: liquidity dried up (${liquidity_usd:.0f})")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue
            if volume_m5 < config["monitor"].get("exit_if_volume_5m_below_usd", 0):
                trade = close_trade(pos, price, "volume_dried_up")
                print(f"📉 SELL {pos.symbol}: 5m volume dried up (${volume_m5:.0f})")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue
            if buys_m5 < config["monitor"].get("exit_if_buys_5m_below", 0):
                trade = close_trade(pos, price, "buy_flow_dried_up")
                print(f"🚪 SELL {pos.symbol}: buy flow dried up ({buys_m5} buys/5m)")
                closed_trade = trade.to_dict()
                closed_trades.append(closed_trade)
                print_closed_trade(closed_trade)
                print_pnl_summary(summarize_pnl(closed_trades))
                continue

        if pnl_pct <= -pos.stop_loss_pct and not pos.tp_armed:
            trade = close_trade(pos, price, "stop_loss")
            print(f"🛑 SELL {pos.symbol}: stop loss hit")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue

        if pos.tp_armed and price <= trailing_stop_price:
            trade = close_trade(pos, price, "trailing_take_profit")
            print(f"🎯 SELL {pos.symbol}: trailing take profit hit")
            closed_trade = trade.to_dict()
            closed_trades.append(closed_trade)
            print_closed_trade(closed_trade)
            print_pnl_summary(summarize_pnl(closed_trades))
            continue

        still_open.append(pos)
    return still_open, closed_trades


def _slice_slots_used(positions):
    """
    Returns the count of distinct token addresses currently open.
    This prevents the bot from stopping because it has many 'slices' 
    for just one or two tokens.
    """
    return len({p.token_address for p in positions})


def _confirm_candidate(candidate, client, config):
    ladder = config.get("ladder", {})
    try:
        pairs = client.token_pairs(candidate["token_address"])
    except Exception:
        return None, "confirm_pair_fetch_fail"
    match = next((p for p in pairs if p.get("pairAddress") == candidate["pair_address"]), None)
    if not match:
        return None, "confirm_pair_missing"
    price = float(match.get("priceUsd") or 0)
    if price <= 0:
        return None, "confirm_bad_price"
    liquidity_usd = float((match.get("liquidity") or {}).get("usd") or 0)
    volume_m5 = float((match.get("volume") or {}).get("m5") or 0)
    buys_m5 = int((((match.get("txns") or {}).get("m5") or {}).get("buys") or 0))
    confirmed = dict(candidate)
    confirmed["price_usd"] = price
    confirmed["liquidity_usd"] = liquidity_usd
    confirmed["volume_m5"] = volume_m5
    confirmed["buys_m5"] = buys_m5
    probe_price = float(candidate.get("price_usd") or 0)
    if probe_price > 0:
        drawdown_pct = ((probe_price - price) / probe_price) * 100
        confirmed["confirm_drawdown_pct"] = drawdown_pct
        if drawdown_pct > ladder.get("confirm_max_drawdown_pct", 999):
            return None, f"confirm_drawdown>{drawdown_pct:.2f}%"
        if ladder.get("require_price_above_probe_avg", False) and price < probe_price:
            return None, "confirm_below_probe_avg"
    if liquidity_usd < ladder.get("confirm_min_liquidity_usd", 0):
        return None, f"confirm_liquidity<{liquidity_usd:.0f}"
    if volume_m5 < ladder.get("confirm_min_volume_5m_usd", 0):
        return None, f"confirm_volume<{volume_m5:.0f}"
    if buys_m5 < ladder.get("confirm_min_buys_5m", 0):
        return None, f"confirm_buys<{buys_m5}"
    if ladder.get("require_liquidity_not_falling", False):
        baseline_liq = float(candidate.get("liquidity_usd") or 0)
        if baseline_liq > 0 and liquidity_usd < baseline_liq:
            return None, "confirm_liquidity_falling"
    return confirmed, None


def hydrate_position(raw):
    ts = now_ms()
    raw.setdefault("opened_at_ms", ts)
    raw.setdefault("last_seen_at_ms", ts)
    return Position(**raw)


def main():
    config = load_config()
    client = DexScreenerClient()
    positions = [hydrate_position(p) for p in load_json(POSITIONS_PATH, [])]
    seen_tokens = set(load_json(SEEN_PATH, []))
    closed_trades = load_json(TRADES_PATH, [])

    discovery_cfg = config.get("discovery", {})
    onchain_discovery = None
    gmgn_discovery = None
    if discovery_cfg.get("source") == "gmgn":
        gmgn_api_key = discovery_cfg.get("api_key")
        if not gmgn_api_key:
            raise ValueError("discovery.api_key is required for GMGN discovery")
        gmgn_discovery = GmgnDiscovery(api_key=gmgn_api_key, chain=discovery_cfg.get("chain", "sol"))
        gmgn_discovery.start(discovery_cfg.get("poll_interval_seconds", 10))
    elif discovery_cfg.get("source") == "onchain":
        quote_symbol = config["filters"].get("require_quote_symbol", "SOL")
        quote_mint = WSOL_MINT if quote_symbol == "SOL" else USDC_MINT
        onchain_discovery = SolanaPoolDiscovery(
            rpc_http_url=discovery_cfg["rpc_http_url"],
            quote_mint=quote_mint,
        )
        onchain_discovery.start(discovery_cfg.get("poll_interval_seconds", 15))

    print("Solana Sniper V2 starting")
    print("=" * 42)
    print("⚙️ STARTUP SETTINGS")
    print("=" * 42)
    print(f"PRESET\n- active: {config.get('preset', 'balanced')}")
    print("FILTERS")
    for k, v in config["filters"].items():
        print(f"- {k}: {v}")
    print(f"STRATEGY\n- mode: {config.get('strategy_mode', 'single_buy')}")
    if config.get("gmgn_filters"):
        print("GMGN_FILTERS")
        for k, v in config["gmgn_filters"].items():
            print(f"- {k}: {v}")
    if config.get("pre_migration_filters"):
        print("PRE_MIGRATION_FILTERS")
        for k, v in config["pre_migration_filters"].items():
            print(f"- {k}: {v}")
    print("TRADE")
    for k, v in config["trade"].items():
        print(f"- {k}: {v}")
    if config.get("ladder"):
        print("LADDER")
        for k, v in config["ladder"].items():
            print(f"- {k}: {v}")
    print("MONITOR")
    for k, v in config["monitor"].items():
        print(f"- {k}: {v}")
    print("PORTFOLIO")
    for k, v in config["portfolio"].items():
        print(f"- {k}: {v}")
    print("DISCOVERY")
    for k, v in config.get("discovery", {}).items():
        print(f"- {k}: {v}")
    print("=" * 42)
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] cycle start, open_positions={len(positions)}")
            # Perform discovery
            try:
                candidates, stats = discover_candidates(client, config, seen_tokens, onchain_discovery, gmgn_discovery)
                
                open_token_count = _slice_slots_used(positions)
                print(
                    "discovery:",
                    f"tokens_held={open_token_count}/{config['portfolio']['max_open_trades']}",
                    f"slices_total={len(positions)}/{config.get('portfolio', {}).get('max_position_slices', 24)}",
                    f"source={stats['source']}",
                    f"profiles={stats['profiles']}",
                    f"onchain={stats['onchain_candidates']}",
                    f"accepted={stats['accepted']}",
                    f"seen={stats['seen']}",
                    f"age={stats['age']}",
                    f"liq={stats['liquidity']}",
                    f"vol={stats['volume']}",
                    f"buys={stats['buys']}",
                    f"fdv={stats['fdv']}",
                    f"blacklist={stats['blacklist']}",
                    f"gmgn_rug={stats['gmgn_rug']}",
                    f"gmgn_bundler={stats['gmgn_bundler']}",
                    f"gmgn_top10={stats['gmgn_top10']}",
                    f"gmgn_open_age={stats['gmgn_open_age']}",
                    f"gmgn_raw_empty={stats['gmgn_raw_empty']}",
                    f"gmgn_prefilter_pass={stats['gmgn_prefilter_pass']}",
                    f"gmgn_prefilter_reject={stats['gmgn_prefilter_reject']}",
                    f"pm_bucket={stats['pm_bucket']}",
                    f"pm_mc={stats['pm_mc']}",
                    f"pm_liq={stats['pm_liq']}",
                    f"pm_progress={stats['pm_progress']}",
                    f"entry_move={stats['entry_move']}",
                )

                if stats.get("raw_examples"):
                    print("raw_examples:", " || ".join(stats["raw_examples"]))
                
                if open_token_count >= config["portfolio"]["max_open_trades"]:
                    print(f"FULL: {open_token_count} tokens held, skipping buy logic for {len(candidates)} candidates")
                else:
                    for candidate in candidates:
                        if _slice_slots_used(positions) >= config["portfolio"]["max_open_trades"]:
                            print("Portfolio full, stopping buy loop")
                            break
                        strategy_mode = config.get("strategy_mode", "single_buy")
                        ladder = config.get("ladder", {})
                        entry_move_text = ""
                        if candidate.get("entry_move_pct") is not None:
                            entry_move_text = f" entry_move={candidate['entry_move_pct']:.1f}%"

                        if strategy_mode in ("ladder_probe_confirm", "pre_migration_ladder"):
                            probe_count = max(1, int(ladder.get("probe_buy_count", 1)))
                            probe_amount = float(ladder.get("probe_buy_usdc", 0))
                            spacing = max(0, int(ladder.get("probe_spacing_seconds", 0)))
                            max_slices = int(config.get("portfolio", {}).get("max_position_slices", config["portfolio"]["max_open_trades"]))
                            slices_left = max_slices - _slice_slots_used(positions)
                            probes_to_place = min(probe_count, max(0, slices_left - 1))
                            if probes_to_place <= 0:
                                print(f"skip {candidate['symbol']}: no slice room for ladder")
                                continue
                            probe_positions = []
                            for idx in range(probes_to_place):
                                pos = open_position(candidate, config, amount_override=probe_amount)
                                positions.append(pos)
                                probe_positions.append(pos)
                                print(
                                    f"🧪 PROBE BUY {idx + 1}/{probes_to_place} {pos.symbol} @ ${pos.entry_price_usd:.10f}"
                                    f" | size=${probe_amount:.2f} age={candidate['pair_age_minutes']:.1f}m"
                                    f" liq=${candidate['liquidity_usd']:.0f}"
                                    f" ca={candidate['token_address']} pair={candidate['pair_address']}"
                                    f" bucket={candidate.get('gmgn_bucket', 'unknown')}"
                                    f" progress={candidate.get('progress_pct', 0):.1f}%"
                                    f" source={candidate.get('discovery_source', 'unknown')}"
                                    f"{entry_move_text}"
                                )
                                if spacing > 0 and idx < probes_to_place - 1:
                                    time.sleep(spacing)
                            confirmed, confirm_reason = _confirm_candidate(candidate, client, config)
                            if confirmed is not None and _slice_slots_used(positions) < max_slices:
                                confirm_amount = float(ladder.get("confirm_buy_usdc", config["trade"]["amount_usdc"]))
                                confirm_pos = open_position(confirmed, config, amount_override=confirm_amount)
                                positions.append(confirm_pos)
                                # seen_tokens.add(candidate["token_address"])
                                confirm_note = ""
                                if confirmed.get("confirm_drawdown_pct") is not None:
                                    confirm_note = f" drawdown={confirmed['confirm_drawdown_pct']:.2f}%"
                                print(
                                    f"✅ CONFIRM BUY {confirm_pos.symbol} @ ${confirm_pos.entry_price_usd:.10f}"
                                    f" | size=${confirm_amount:.2f} age={confirmed['pair_age_minutes']:.1f}m"
                                    f" liq=${confirmed['liquidity_usd']:.0f} vol5m=${confirmed['volume_m5']:.0f} buys5m={confirmed['buys_m5']}"
                                    f" ca={confirmed['token_address']} pair={confirmed['pair_address']}"
                                    f" bucket={confirmed.get('gmgn_bucket', 'unknown')} progress={confirmed.get('progress_pct', 0):.1f}%"
                                    f"{confirm_note}"
                                )
                            else:
                                # seen_tokens.add(candidate['token_address'])
                                kept_positions = []
                                probe_keys = {(p.token_address, p.pair_address, p.opened_at_ms, p.amount_usdc) for p in probe_positions}
                                for pos in positions:
                                    pos_key = (pos.token_address, pos.pair_address, pos.opened_at_ms, pos.amount_usdc)
                                    if pos_key in probe_keys:
                                        trade = close_trade(pos, pos.last_price_usd or pos.entry_price_usd, "confirm_failed")
                                        print(f"❌ CONFIRM SKIP {candidate['symbol']}: {confirm_reason} -> closing probe")
                                        closed_trade = trade.to_dict()
                                        closed_trades.append(closed_trade)
                                        print_closed_trade(closed_trade)
                                    else:
                                        kept_positions.append(pos)
                                positions = kept_positions
                                print_pnl_summary(summarize_pnl(closed_trades))
                        else:
                            pos = open_position(candidate, config)
                            positions.append(pos)
                            seen_tokens.add(candidate["token_address"])
                            print(
                                f"🚀 PAPER BUY {pos.symbol} @ ${pos.entry_price_usd:.10f}"
                                f" | age={candidate['pair_age_minutes']:.1f}m"
                                f" liq=${candidate['liquidity_usd']:.0f}"
                                f" ca={candidate['token_address']}"
                                f" pair={candidate['pair_address']}"
                                f" source={candidate.get('discovery_source', 'unknown')}"
                                f"{entry_move_text}"
                            )
            except Exception as e:
                print(f"discovery_error: {e}")

            try:
                positions, closed_trades = monitor_positions(client, positions, config, closed_trades)
            except Exception as e:
                print(f"monitor_error: {e}")

            save_json(POSITIONS_PATH, [p.to_dict() for p in positions])
            save_json(TRADES_PATH, closed_trades)
            save_json(SEEN_PATH, sorted(seen_tokens))
            save_json(PNL_PATH, summarize_pnl(closed_trades))
        except Exception as e:
            print(f"cycle_error: {e}")
        time.sleep(config["monitor"]["price_poll_interval_seconds"])


if __name__ == "__main__":
    main()
