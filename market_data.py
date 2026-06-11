"""Alpaca market-data explorer (free tier).

Pulls stocks, ETFs, crypto and (best effort) options, computes per-asset metrics
and prints a pandas DataFrame. Standalone scratch/analysis tool; not part of the
README pipeline. Needs ALPACA_API_KEY / ALPACA_SECRET_KEY in the environment.

Run:  python market_data.py
"""

import os
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta, timezone

from dotenv import load_dotenv

from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import (
    CryptoBarsRequest,
    CryptoLatestQuoteRequest,
    StockBarsRequest,
    StockLatestQuoteRequest,
)
from alpaca.data.timeframe import TimeFrame

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

NOW = datetime.now(tz=timezone.utc)
START = NOW - timedelta(days=40)   # extra buffer for weekends/holidays
END = NOW - timedelta(minutes=20)  # stay outside 15-min IEX window

STOCKS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", "JPM", "BAC", "XOM"]
ETFS   = ["SPY", "QQQ", "IWM", "DIA", "GLD", "TLT", "XLF", "XLE", "ARKK"]
CRYPTO = ["BTC/USD", "ETH/USD", "SOL/USD", "AVAX/USD", "DOGE/USD", "LINK/USD"]


def _metrics(symbol, bars, quote, asset_type):
    if len(bars) < 2:
        return None
    closes  = [b.close  for b in bars]
    volumes = [b.volume for b in bars]
    series  = pd.Series(closes)
    daily_ret = series.pct_change().dropna()

    if quote and quote.bid_price and quote.ask_price:
        bid, ask = quote.bid_price, quote.ask_price
        mid = (bid + ask) / 2
        spread_pct = (ask - bid) / mid * 100
    else:
        bid = ask = None
        mid = closes[-1]
        spread_pct = None

    avg_vol  = float(np.mean(volumes))
    roll_max = series.cummax()
    max_dd   = ((series - roll_max) / roll_max * 100).min()

    return {
        "symbol":             symbol,
        "type":               asset_type,
        "last_price":         round(mid, 4),
        "bid":                bid,
        "ask":                ask,
        "spread_pct":         round(spread_pct, 3) if spread_pct is not None else None,
        "change_pct":         round((mid - closes[-2]) / closes[-2] * 100, 2),
        "volume":             int(volumes[-1]),
        "avg_vol_30d":        int(avg_vol),
        "vol_ratio":          round(volumes[-1] / avg_vol, 2) if avg_vol else None,
        "return_5d_pct":      round((closes[-1] / closes[max(-6, -len(closes))] - 1) * 100, 2),
        "return_30d_pct":     round((closes[-1] / closes[0] - 1) * 100, 2),
        "volatility_ann_pct": round(daily_ret.std() * np.sqrt(252) * 100, 2),
        "max_drawdown_pct":   round(max_dd, 2),
    }


# ── Equities (stocks + ETFs) ───────────────────────────────────────────────────
stock_client   = StockHistoricalDataClient(API_KEY, SECRET_KEY)
equity_symbols = STOCKS + ETFS

bars_data = stock_client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=equity_symbols,
    timeframe=TimeFrame.Day,
    start=START,
    end=END,
    feed="iex",
)).data

quotes_data = stock_client.get_stock_latest_quote(
    StockLatestQuoteRequest(symbol_or_symbols=equity_symbols, feed="iex")
)

rows = []
for sym in equity_symbols:
    bars = list(bars_data.get(sym, []))
    row  = _metrics(sym, bars, quotes_data.get(sym), "etf" if sym in ETFS else "stock")
    if row:
        rows.append(row)

# ── Crypto ─────────────────────────────────────────────────────────────────────
crypto_client = CryptoHistoricalDataClient()

crypto_bars = crypto_client.get_crypto_bars(CryptoBarsRequest(
    symbol_or_symbols=CRYPTO,
    timeframe=TimeFrame.Day,
    start=START,
)).data

crypto_quotes = crypto_client.get_crypto_latest_quote(
    CryptoLatestQuoteRequest(symbol_or_symbols=CRYPTO)
)

for sym in CRYPTO:
    bars = list(crypto_bars.get(sym, []))
    row  = _metrics(sym, bars, crypto_quotes.get(sym), "crypto")
    if row:
        rows.append(row)

# ── Options (near-ATM, 7–45 DTE) — graceful fallback if not on free tier ──────
try:
    from alpaca.data import OptionHistoricalDataClient
    from alpaca.data.requests import OptionLatestQuoteRequest
    from alpaca.trading import TradingClient
    from alpaca.trading.requests import GetOptionContractsRequest

    trading    = TradingClient(API_KEY, SECRET_KEY, paper=True)
    opt_client = OptionHistoricalDataClient(API_KEY, SECRET_KEY)

    for underlying in ["AAPL", "SPY", "QQQ"]:
        q    = quotes_data.get(underlying)
        spot = ((q.bid_price + q.ask_price) / 2) if q else None

        result    = trading.get_option_contracts(GetOptionContractsRequest(
            underlying_symbols=[underlying],
            expiration_date_gte=date.today() + timedelta(days=7),
            expiration_date_lte=date.today() + timedelta(days=45),
            status="active",
        ))
        contracts = (
            result.option_contracts if hasattr(result, "option_contracts") else list(result)
        )

        if spot:
            contracts = sorted(contracts, key=lambda c: abs(float(c.strike_price) - spot))

        contract_syms = [c.symbol for c in contracts[:12]]
        if not contract_syms:
            continue

        opt_quotes = opt_client.get_option_latest_quote(
            OptionLatestQuoteRequest(symbol_or_symbols=contract_syms)
        )

        for sym, oq in opt_quotes.items():
            if not oq.bid_price or not oq.ask_price:
                continue
            mid        = (oq.bid_price + oq.ask_price) / 2
            spread_pct = (oq.ask_price - oq.bid_price) / mid * 100 if mid else None
            rows.append({
                "symbol":             sym,
                "type":               "option",
                "last_price":         round(mid, 4),
                "bid":                oq.bid_price,
                "ask":                oq.ask_price,
                "spread_pct":         round(spread_pct, 2) if spread_pct else None,
                "change_pct":         None,
                "volume":             None,
                "avg_vol_30d":        None,
                "vol_ratio":          None,
                "return_5d_pct":      None,
                "return_30d_pct":     None,
                "volatility_ann_pct": None,
                "max_drawdown_pct":   None,
            })

except Exception as e:
    print(f"[options] skipped — {e}")

# ── Final DataFrame ────────────────────────────────────────────────────────────
df = (
    pd.DataFrame(rows)
    .sort_values(["type", "symbol"])
    .reset_index(drop=True)
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)
pd.set_option("display.float_format", "{:.4f}".format)
print(df.to_string(index=False))