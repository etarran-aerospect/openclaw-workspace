# Prediction Bot V1 notes

## Repo audit summary

### 1. polymarket/agents
Most useful as a reference architecture and connector toolkit.
Best value:
- market and API integration patterns
- agent/tooling structure
- data source modularity
Less useful for first build:
- too broad and agent-oriented for a tight first trading bot

### 2. aulekator/Polymarket-BTC-15-Minute-Trading-Bot
Most useful as a strategy-system reference.
Best value:
- multi-signal pipeline
- explicit risk layer
- simulation/live separation
Less useful for first build:
- likely overbuilt for v1
- too specialized around BTC 15-minute markets

### 3. warproxxx/poly-maker
Most useful as an execution and market-making reference.
Best value:
- order book and position management ideas
- practical Polymarket operational details
Less useful for first build:
- market making is a different strategy than directional/event trading
- extra operational complexity

### 4. hyperliquid-python-sdk
Useful as SDK base only.
Best value:
- direct Hyperliquid API access
- future phase-2 integration
Less useful for first build:
- not a prediction-market architecture by itself
- better treated as execution plumbing later

## Recommendation
Start with Polymarket-focused paper trading bot first.
Add Hyperliquid module second.

## V1 architecture
1. Market discovery
   - fetch active Polymarket markets
   - normalize yes/no markets
   - optional category filters

2. Feature layer
   - market price / implied probability
   - recent movement
   - spread / liquidity snapshot
   - optional external signal adapters later

3. Strategy layer
   - simple rule-based edge detector first
   - no LLM dependency in core execution loop

4. Portfolio and risk
   - max position per market
   - max total exposure
   - no entry near resolution by default
   - stop trading on stale data

5. Paper execution
   - simulate entry and exit at configurable slippage
   - full trade log

6. Reporting
   - open positions
   - closed trades
   - cumulative PnL

## Initial target
Build a clean paper-trading framework first, not a live-money bot.
