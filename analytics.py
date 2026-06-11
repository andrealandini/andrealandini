"""Risk and credit analytics charts (SIMULATED data, illustrative only).

Writes the Risk and Credit Markets panels to ./charts/:
  Risk            : var_fan, es_cvar, pnl_hist, rolling_var
  Credit Markets  : spread_term, spread_heatmap, oas_waterfall

Run:  python analytics.py
"""

import math
import os

import numpy as np

from svgkit import (
    Chart, GREEN, RED, AMBER, CYAN, MUTED, esc, nice_ticks, heat_color,
)
# ══════════════════════════════════════════════════════════════════════════════
# 1. VaR FAN CHART
# ══════════════════════════════════════════════════════════════════════════════
def chart_var_fan():
    rng = np.random.default_rng(7)
    H, N, sigma = 20, 8000, 0.012
    steps = rng.normal(0.0002, sigma, (N, H))
    cum = np.column_stack([np.zeros(N), (np.cumprod(1 + steps, axis=1) - 1)]) * 100
    xs = np.arange(H + 1)
    pct = lambda q: np.percentile(cum, q, axis=0)
    med = pct(50)
    lo68, hi68 = pct(16), pct(84)
    lo95, hi95 = pct(2.5), pct(97.5)
    lo99, hi99 = pct(0.5), pct(99.5)

    c = Chart("VaR FAN CHART", "20D · 8k paths · synthetic")
    c.set_xlim(0, H)
    c.set_ylim(lo99.min() * 1.08, hi99.max() * 1.08)
    yt = nice_ticks(c.ylim[0], c.ylim[1], 6)
    c.grid_axes([0, 5, 10, 15, 20], yt, xfmt=lambda v: f"{v:g}",
                yfmt=lambda v: f"{v:+.0f}", xlabel="Horizon (days)", ylabel="P&L (%)")

    c.add(c.band(xs, lo99, hi99, GREEN, 0.07, begin=0.15, breathe=True))
    c.add(c.band(xs, lo95, hi95, GREEN, 0.12, begin=0.35, breathe=True))
    c.add(c.band(xs, lo68, hi68, GREEN, 0.20, begin=0.55, breathe=True))
    c.add(c.line(list(zip(xs, med)), GREEN, 2.2, dur=1.6, begin=0.2, flow=True, flow_color=GREEN))
    c.add(c.line(list(zip(xs, lo95)), AMBER, 1.4, glow=False, dur=1.0, begin=1.1, dash="5 3"))
    c.add(c.line(list(zip(xs, lo99)), RED, 1.4, glow=False, dur=1.0, begin=1.3, dash="5 3"))

    var95, var99 = -lo95[-1], -lo99[-1]
    c.add(c.readout([(AMBER, f"VaR95  {var95:.1f}%"), (RED, f"VaR99  {var99:.1f}%")],
                    c.x1 - 6, c.yt + 14, anchor="end", begin=2.0))
    c.add(c.legend([(GREEN, "median"), (AMBER, "95% bound"), (RED, "99% bound")], c.x0 + 8, c.yt + 14))
    return c.save("var_fan.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 2. EXPECTED SHORTFALL (CVaR) OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
def _kde(samples, grid, bw):
    s = samples[:, None]
    g = grid[None, :]
    k = np.exp(-0.5 * ((g - s) / bw) ** 2)
    return k.sum(0) / (len(samples) * bw * math.sqrt(2 * math.pi))


def chart_es_cvar():
    rng = np.random.default_rng(3)
    # fat-tailed P&L: normal core + occasional large losses
    core = rng.normal(0.04, 1.0, 18000)
    shock = rng.normal(-3.2, 1.4, 2000)
    pnl = np.concatenate([core, shock])

    var95 = np.percentile(pnl, 5)
    var99 = np.percentile(pnl, 1)
    es95 = pnl[pnl <= var95].mean()
    es99 = pnl[pnl <= var99].mean()

    grid = np.linspace(pnl.min(), np.percentile(pnl, 99.5), 240)
    dens = _kde(pnl, grid, bw=0.35)

    c = Chart("EXPECTED SHORTFALL (CVaR)", "ES vs VaR · synthetic")
    c.set_xlim(grid.min(), grid.max())
    c.set_ylim(0, dens.max() * 1.15)
    c.grid_axes(nice_ticks(grid.min(), grid.max(), 6), nice_ticks(0, dens.max() * 1.15, 4),
                xfmt=lambda v: f"{v:+.0f}", yfmt=lambda v: f"{v:.2f}",
                xlabel="P&L (%)", ylabel="density")

    # shaded tail beyond VaR95
    mask = grid <= var95
    xs_t = grid[mask]
    if len(xs_t) > 1:
        c.add(c.band(xs_t, np.zeros(len(xs_t)), dens[mask], RED, 0.22, begin=0.9, dur=0.9))
    c.add(c.line(list(zip(grid, dens)), GREEN, 2.0, dur=1.7, begin=0.1, flow=True, flow_color=GREEN, flow_dur=5.0))

    c.add(c.vline(var95, AMBER, begin=1.4))
    c.add(c.vline(es95, RED, begin=1.7))
    c.add(c.vline(var99, "#ff8a3d", begin=2.0, dash="2 3", pulse=False))
    c.add(c.vline(es99, "#c0392b", begin=2.3, dash="2 3"))
    c.add(c.readout([(AMBER, f"VaR95  {var95:.1f}"), (RED, f"ES95   {es95:.1f}"),
                     ("#ff8a3d", f"VaR99  {var99:.1f}"), ("#c0392b", f"ES99   {es99:.1f}")],
                    c.x1 - 6, c.yt + 14, anchor="end", begin=2.4))
    c.add(c.legend([(GREEN, "P&L density"), (AMBER, "VaR"), (RED, "ES / CVaR")], c.x0 + 8, c.yt + 14))
    return c.save("es_cvar.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 3. P&L HISTOGRAM WITH VaR / ES LINES
# ══════════════════════════════════════════════════════════════════════════════
def chart_pnl_hist():
    rng = np.random.default_rng(5)
    core = rng.normal(0.05, 1.0, 9000)
    shock = rng.normal(-2.6, 1.3, 1200)
    pnl = np.concatenate([core, shock])

    var95 = np.percentile(pnl, 5)
    es95 = pnl[pnl <= var95].mean()

    counts, edges = np.histogram(pnl, bins=46)
    centers = (edges[:-1] + edges[1:]) / 2
    cmax = counts.max()

    c = Chart("P&L DISTRIBUTION", "VaR/ES overlay · synthetic")
    c.set_xlim(edges[0], edges[-1])
    c.set_ylim(0, cmax * 1.12)
    c.grid_axes(nice_ticks(edges[0], edges[-1], 6), nice_ticks(0, cmax * 1.12, 4),
                xfmt=lambda v: f"{v:+.0f}", yfmt=lambda v: f"{v/1000:.1f}k" if v >= 1000 else f"{v:.0f}",
                xlabel="P&L (%)", ylabel="frequency")

    bw = (c.sx(edges[1]) - c.sx(edges[0])) * 0.86
    for i, (cx, ct) in enumerate(zip(centers, counts)):
        if ct == 0:
            continue
        color = RED if cx < var95 else (AMBER if cx < 0 else GREEN)
        xpx = c.sx(cx) - bw / 2
        c.add(c.bar(xpx, bw, c.sy(ct), c.sy(0), color, begin=0.2 + i * 0.012, dur=0.6, opacity=0.92))

    c.add(c.vline(var95, AMBER, begin=1.3))
    c.add(c.vline(es95, RED, begin=1.6))
    c.add(c.readout([(AMBER, f"VaR95  {var95:.1f}%"), (RED, f"ES95   {es95:.1f}%")],
                    c.x1 - 6, c.yt + 14, anchor="end", begin=1.9))
    c.add(c.legend([(GREEN, "gains"), (AMBER, "losses"), (RED, "tail < VaR")], c.x0 + 8, c.yt + 14))
    return c.save("pnl_hist.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4. ROLLING VaR (time series, with stress regime + scanner dot)
# ══════════════════════════════════════════════════════════════════════════════
def chart_rolling_var():
    rng = np.random.default_rng(9)
    T = 252
    vol = np.full(T, 0.009)
    vol[110:150] = np.linspace(0.009, 0.032, 40)   # stress ramp-up
    vol[150:175] = np.linspace(0.032, 0.012, 25)   # decay
    rets = rng.normal(0, 1, T) * vol
    win = 40
    var = np.array([
        -np.percentile(rets[max(0, t - win):t + 1], 5) * 100 for t in range(T)
    ])
    xs = np.arange(T)

    c = Chart("ROLLING VaR (95%)", "40D window · 1Y · synthetic", width=560, height=340)
    c.set_xlim(0, T - 1)
    c.set_ylim(0, var.max() * 1.18)
    c.grid_axes(nice_ticks(0, T - 1, 6), nice_ticks(0, var.max() * 1.18, 5),
                xfmt=lambda v: f"{int(v)}", yfmt=lambda v: f"{v:.1f}",
                xlabel="Trading day", ylabel="VaR (%)")

    # stress window shading
    sx0, sx1 = c.sx(110), c.sx(175)
    c.add(f'<rect x="{sx0:.1f}" y="{c.yt}" width="{sx1 - sx0:.1f}" height="{c.yb - c.yt:.1f}" '
          f'fill="{RED}" opacity="0"><animate attributeName="opacity" to="0.08" dur="0.8s" begin="0.4s" fill="freeze"/></rect>')
    c.add(f'<text x="{(sx0 + sx1) / 2:.1f}" y="{c.yt + 12:.1f}" fill="{RED}" font-size="9" text-anchor="middle" '
          f'opacity="0"><animate attributeName="opacity" to="0.8" dur="0.8s" begin="1.6s" fill="freeze"/>STRESS</text>')

    pts = list(zip(xs, var))
    path_d = "M " + " L ".join(f"{c.sx(x):.1f} {c.sy(y):.1f}" for x, y in pts)
    c.add(f'<path id="varline" d="{path_d}" fill="none" stroke="{GREEN}" stroke-width="2" '
          f'filter="url(#glow)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
          f'<animate attributeName="stroke-dashoffset" from="1" to="0" dur="2.4s" begin="0.3s" fill="freeze"/></path>')
    # area under the line
    area = f'M {c.sx(0):.1f} {c.sy(0):.1f} ' + " ".join(f"{c.sx(x):.1f} {c.sy(y):.1f}" for x, y in pts) + f' {c.sx(T-1):.1f} {c.sy(0):.1f} Z'
    c.add(f'<path d="{area}" fill="{GREEN}" opacity="0"><animate attributeName="opacity" to="0.10" dur="1.0s" begin="2.4s" fill="freeze"/></path>')

    # sweeping scanner dot riding the line forever
    c.add(f'<circle r="3.6" fill="{CYAN}" filter="url(#glow)">'
          f'<animateMotion dur="6s" begin="2.6s" repeatCount="indefinite" rotate="0">'
          f'<mpath href="#varline"/></animateMotion></circle>')

    peak = var.argmax()
    c.add(c.tag(peak, var[peak], f"peak {var[peak]:.1f}%", CYAN, anchor="start", dy=-6, begin=2.6))
    return c.save("rolling_var.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 5. CREDIT SPREAD TERM STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
def chart_spread_term():
    mats = np.array([1, 2, 3, 5, 7, 10, 20, 30])
    curves = {
        "AAA": (35, 0.85, GREEN),
        "IG (BBB)": (95, 1.9, CYAN),
        "HY (BB)": (290, 3.2, AMBER),
        "HY (B)":  (520, 4.0, RED),
    }
    c = Chart("CREDIT SPREAD TERM STRUCTURE", "by rating · synthetic")
    c.set_xlim(0, 31)
    ymax = 0
    series = {}
    for name, (base, slope, color) in curves.items():
        s = base + slope * (mats ** 0.92) * 8 + np.log1p(mats) * 6
        series[name] = (s, color)
        ymax = max(ymax, s.max())
    c.set_ylim(0, ymax * 1.12)
    c.grid_axes(list(mats), nice_ticks(0, ymax * 1.12, 6),
                xfmt=lambda v: f"{int(v)}Y", yfmt=lambda v: f"{int(v)}",
                xlabel="Maturity", ylabel="Spread (bps)")

    for i, (name, (s, color)) in enumerate(series.items()):
        c.add(c.line(list(zip(mats, s)), color, 2.0, dur=1.6, begin=0.3 + i * 0.25,
                     flow=True, flow_color=color, flow_dur=4.0 + i * 0.4))
        for m, y in zip(mats, s):
            c.add(c.dot(m, y, color, r=2.6, begin=1.6 + i * 0.25, glow=False))
        c.add(c.tag(mats[-1], s[-1], name, color, anchor="end", dy=-5, begin=2.0 + i * 0.2))
    return c.save("spread_term.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 6. SPREAD HEATMAP (issuers × maturities)
# ══════════════════════════════════════════════════════════════════════════════
def chart_spread_heatmap():
    rng = np.random.default_rng(11)
    issuers = ["AAPL", "MSFT", "JPM", "T", "F", "GM", "X", "CCL"]
    mats = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y"]
    base = np.array([40, 45, 80, 150, 240, 300, 360, 430], dtype=float)
    slope = np.linspace(0.7, 1.45, len(mats))
    M = base[:, None] * slope[None, :] + rng.normal(0, 10, (len(issuers), len(mats)))
    M = np.clip(M, 15, 700)
    vmin, vmax = M.min(), M.max()

    w, h = 560, 388
    left, top = 70, 60
    cw = (w - left - 80) / len(mats)
    ch = (h - top - 46) / len(issuers)

    c = Chart("SPREAD HEATMAP", "issuer × maturity · bps · synthetic", width=w, height=h)
    c.body = []  # custom layout, no axes

    for i, iss in enumerate(issuers):
        cy = top + i * ch
        c.add(f'<text x="{left - 8}" y="{cy + ch/2 + 3:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">{esc(iss)}</text>')
        for j, mt in enumerate(mats):
            cx = left + j * cw
            val = M[i, j]
            t = (val - vmin) / (vmax - vmin)
            color = heat_color(t)
            begin = 0.2 + (i + j) * 0.06
            c.add(f'<rect x="{cx + 1:.1f}" y="{cy + 1:.1f}" width="{cw - 2:.1f}" height="{ch - 2:.1f}" rx="2" '
                  f'fill="{color}" opacity="0">'
                  f'<animate attributeName="opacity" to="0.92" dur="0.5s" begin="{begin}s" fill="freeze"/>'
                  f'<animate attributeName="opacity" values="0.92;0.74;0.92" dur="{3.0 + (i + j) % 4 * 0.4:.1f}s" '
                  f'begin="{begin + 0.8:.1f}s" repeatCount="indefinite"/></rect>')
            c.add(f'<text x="{cx + cw/2:.1f}" y="{cy + ch/2 + 3:.1f}" fill="#0d1117" font-size="9" font-weight="bold" '
                  f'text-anchor="middle" opacity="0"><animate attributeName="opacity" to="1" dur="0.5s" begin="{begin + 0.25}s" fill="freeze"/>{val:.0f}</text>')
    for j, mt in enumerate(mats):
        cx = left + j * cw
        c.add(f'<text x="{cx + cw/2:.1f}" y="{top + len(issuers)*ch + 16:.1f}" fill="{MUTED}" font-size="10" text-anchor="middle">{esc(mt)}</text>')

    # colorbar
    bx, by, bw_, bh_ = w - 26, top, 12, len(issuers) * ch
    c.add(f'<defs><linearGradient id="cbar" x1="0" y1="1" x2="0" y2="0">'
          f'<stop offset="0" stop-color="{heat_color(0)}"/><stop offset="0.5" stop-color="{heat_color(0.5)}"/>'
          f'<stop offset="1" stop-color="{heat_color(1)}"/></linearGradient></defs>')
    c.add(f'<rect x="{bx}" y="{by}" width="{bw_}" height="{bh_:.1f}" rx="2" fill="url(#cbar)" opacity="0.9"/>')
    c.add(f'<text x="{bx + bw_/2:.1f}" y="{by - 4}" fill="{MUTED}" font-size="8" text-anchor="middle">{vmax:.0f}</text>')
    c.add(f'<text x="{bx + bw_/2:.1f}" y="{by + bh_ + 10:.1f}" fill="{MUTED}" font-size="8" text-anchor="middle">{vmin:.0f}</text>')
    return c.save("spread_heatmap.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 7. Z-SPREAD / OAS WATERFALL
# ══════════════════════════════════════════════════════════════════════════════
def chart_oas_waterfall():
    # additive decomposition of a credit spread into components
    steps = [
        ("Swap",       25,  "add"),
        ("Liquidity",  38,  "add"),
        ("Credit",     128, "add"),
        ("Z-spread",   None, "total"),
        ("Option",    -27,  "sub"),
        ("OAS",        None, "total"),
    ]
    c = Chart("Z-SPREAD / OAS WATERFALL", "spread decomposition · bps · synthetic")
    labels = [s[0] for s in steps]

    # compute running totals
    running = 0.0
    bars = []  # (label, y_lo, y_hi, kind)
    for label, val, kind in steps:
        if kind == "add":
            bars.append((label, running, running + val, val, kind))
            running += val
        elif kind == "sub":
            bars.append((label, running + val, running, val, kind))
            running += val
        else:  # total
            bars.append((label, 0, running, running, kind))

    ymax = max(b[2] for b in bars) * 1.15
    c.set_xlim(-0.5, len(bars) - 0.5)
    c.set_ylim(0, ymax)
    c.grid_axes([], nice_ticks(0, ymax, 6), yfmt=lambda v: f"{int(v)}", ylabel="Spread (bps)")

    n = len(bars)
    slot = (c.x1 - c.x0) / n
    bw = slot * 0.56
    prev_top_px = None
    for i, (label, ylo, yhi, val, kind) in enumerate(bars):
        cx = c.x0 + slot * (i + 0.5)
        xpx = cx - bw / 2
        ytop = c.sy(yhi)
        ybase = c.sy(ylo)
        color = {"add": GREEN, "sub": RED, "total": CYAN}[kind]
        begin = 0.3 + i * 0.45
        c.add(c.bar(xpx, bw, ytop, ybase, color, begin=begin, dur=0.6, opacity=0.9))
        # value label
        sign = "+" if kind == "add" else ("−" if kind == "sub" else "")
        c.add(f'<text x="{cx:.1f}" y="{ytop - 5:.1f}" fill="{color}" font-size="10" font-weight="bold" '
              f'text-anchor="middle" opacity="0"><animate attributeName="opacity" to="1" dur="0.4s" '
              f'begin="{begin + 0.5}s" fill="freeze"/>{sign}{abs(val):.0f}</text>')
        # x label
        c.add(f'<text x="{cx:.1f}" y="{c.yb + 15:.1f}" fill="{MUTED}" font-size="9" text-anchor="middle">{esc(label)}</text>')
        # connector to next bar
        if prev_top_px is not None and kind != "total":
            pass
        # dotted connector from running level to next
        if i < n - 1:
            connect_y = c.sy(running_level(bars, i))
            c.add(f'<line x1="{cx + bw/2:.1f}" y1="{connect_y:.1f}" x2="{cx + slot - bw/2:.1f}" y2="{connect_y:.1f}" '
                  f'stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 2" opacity="0">'
                  f'<animate attributeName="opacity" to="0.5" dur="0.4s" begin="{begin + 0.6}s" fill="freeze"/></line>')
    return c.save("oas_waterfall.svg")


def running_level(bars, i):
    """Top of the cumulative stack after bar i (for connector lines)."""
    label, ylo, yhi, val, kind = bars[i]
    if kind == "total":
        return yhi
    return yhi if kind == "add" else ylo


# ══════════════════════════════════════════════════════════════════════════════
def main():
    charts = [
        chart_var_fan, chart_es_cvar, chart_pnl_hist, chart_rolling_var,
        chart_spread_term, chart_spread_heatmap, chart_oas_waterfall,
    ]
    for fn in charts:
        path = fn()
        print(f"wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
