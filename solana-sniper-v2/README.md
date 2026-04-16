# Solana Sniper V2

Paper-first Solana meme token monitor and sniper scaffold.

## Status
Early rebuild scaffold intended to replace the unreliable CoinGecko Demo based bot.

## Design goals
- Reliable fresh-pair discovery
- Reliable pair-level price monitoring
- Paper trading first
- Clean path to real execution later

## Planned data flow
1. Discover fresh Solana pairs from a better market data source
2. Normalize pair metadata
3. Filter by liquidity, age, volume, and activity
4. Open paper positions
5. Monitor pair prices on a fixed cadence
6. Close on TP, SL, trailing stop, or stale timeout

## Next build target
Initial implementation will likely use DexScreener-style pair discovery and monitoring because it is simpler and better aligned to meme-token pair tracking than the current CoinGecko Demo approach.
