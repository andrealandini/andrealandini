"""Fetch market data from Alpaca (free tier) and render a scrolling ticker.svg.

Run locally with a .env (ALPACA_API_KEY / ALPACA_SECRET_KEY) or in CI with those
values provided as environment variables. Writes ticker.svg next to this file.
"""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

NOW = datetime.now(tz=timezone.utc)
START = NOW - timedelta(days=10)   # enough for 2+ trading days
END = NOW - timedelta(minutes=20)  # stay outside the 15-min IEX window

STOCKS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META"]
ETFS   = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
CRYPTO = ["BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD"]

# ── Visual config ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 40
FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.60        # monospace advance width estimate
SPEED_PX_S = 55                  # scroll speed
BG = "#0d1117"
UP, DOWN, FLAT = "#00ff41", "#ff4d4d", "#8b949e"
DIM = "#30363d"
SEP = "  ◈  "               # ◈ between items


def last_change_pct(bars):
    """Percent change between the last two daily closes."""
    closes = [b.close for b in bars]
    if len(closes) < 2 or not closes[-2]:
        return None
    return (closes[-1] / closes[-2] - 1) * 100


def collect():
    items = []  # (display_symbol, change_pct)

    # Equities (stocks + ETFs) — IEX feed is free
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    equities = STOCKS + ETFS
    bars = stock_client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=equities,
        timeframe=TimeFrame.Day,
        start=START,
        end=END,
        feed="iex",
    )).data
    for sym in equities:
        chg = last_change_pct(list(bars.get(sym, [])))
        if chg is not None:
            items.append((sym, chg))

    # Crypto — keyless, 24/7
    crypto_client = CryptoHistoricalDataClient()
    cbars = crypto_client.get_crypto_bars(CryptoBarsRequest(
        symbol_or_symbols=CRYPTO,
        timeframe=TimeFrame.Day,
        start=START,
    )).data
    for sym in CRYPTO:
        chg = last_change_pct(list(cbars.get(sym, [])))
        if chg is not None:
            items.append((sym.split("/")[0], chg))

    return items


def fmt(symbol, chg):
    arrow = "▲" if chg > 0.05 else "▼" if chg < -0.05 else "■"
    color = UP if chg > 0.05 else DOWN if chg < -0.05 else FLAT
    label = f"{arrow} {symbol} {chg:+.2f}%"
    return label, color


def build_svg(items):
    if not items:
        items = [("NO DATA", 0.0)]

    # Build one copy of the marquee as a list of (text, color) tspans.
    parts = []
    plain = ""
    for i, (sym, chg) in enumerate(items):
        label, color = fmt(sym, chg)
        parts.append((label, color))
        plain += label
        if i != len(items) - 1:
            parts.append((SEP, DIM))
            plain += SEP
    parts.append((SEP, DIM))   # trailing sep so the loop joins cleanly
    plain += SEP

    one_copy_w = len(plain) * CHAR_W
    duration = max(20, round(one_copy_w / SPEED_PX_S))

    def render(parts):
        out = []
        for text, color in parts:
            esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f'<tspan fill="{color}">{esc}</tspan>')
        return "".join(out)

    # Two back-to-back copies → seamless wrap when x animates by -one_copy_w.
    spans = render(parts) + render(parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>
  <rect x="0" y="0" width="{WIDTH}" height="1" fill="{UP}" opacity="0.4"/>
  <rect x="0" y="{HEIGHT - 1}" width="{WIDTH}" height="1" fill="{UP}" opacity="0.4"/>

  <clipPath id="clip"><rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}"/></clipPath>

  <text font-family="monospace" font-size="{FONT_SIZE}" y="25" clip-path="url(#clip)" xml:space="preserve">{spans}<animate attributeName="x" from="0" to="-{one_copy_w:.0f}" dur="{duration}s" repeatCount="indefinite"/></text>
</svg>
'''


def main():
    items = collect()
    svg = build_svg(items)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ticker.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {path} with {len(items)} items.")


if __name__ == "__main__":
    main()
