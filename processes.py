"""Animated (SMIL) SVG gallery of the stochastic processes used in quant
finance: Brownian motion, geometric Brownian motion and Merton jump-diffusion.
Same terminal theme and draw-on animation as the ticker and analytics charts.

Reuses the SVG toolkit from svgkit.py. Writes to ./charts/ (sp_*.svg).

Run:  python processes.py
"""

import math

import numpy as np

from svgkit import (
    Chart, GREEN, RED, AMBER, CYAN, MUTED, esc, nice_ticks,
)

PATHS = [GREEN, CYAN, AMBER, "#ff8a3d", "#a974ff"]


def _new(title, sde, width=540, height=300):
    return Chart(title, sde, width=width, height=height, pad=(52, 18, 44, 58))


def _caption(c, use):
    return (f'<text x="{c.x0}" y="{c.h - 12}" fill="{GREEN}" font-size="10" opacity="0">'
            f'<animate attributeName="opacity" to="0.9" dur="0.6s" begin="1.6s" fill="freeze"/>'
            f'▸ {esc(use)}</text>')


def _axes(c, ylabel, yfmt):
    c.grid_axes(nice_ticks(c.xlim[0], c.xlim[1], 5), nice_ticks(c.ylim[0], c.ylim[1], 5),
                xfmt=lambda v: f"{v:g}", yfmt=yfmt, xlabel="", ylabel=ylabel)


# ── 1. Wiener process / Brownian motion ────────────────────────────────────────
def brownian():
    rng = np.random.default_rng(1)
    n, steps = 5, 220
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    W = np.column_stack([np.zeros(n), np.cumsum(rng.normal(0, math.sqrt(dt), (n, steps)), axis=1)])

    c = _new("WIENER PROCESS", "dWₜ ~ 𝒩(0, dt)")
    c.set_xlim(0, 1)
    c.set_ylim(W.min() * 1.1, W.max() * 1.1)
    _axes(c, "Wₜ", lambda v: f"{v:+.1f}")
    c.add(f'<line x1="{c.x0}" y1="{c.sy(0):.1f}" x2="{c.x1}" y2="{c.sy(0):.1f}" stroke="{MUTED}" stroke-dasharray="3 3" stroke-width="1" opacity="0.4"/>')
    for i in range(n):
        col = PATHS[i % len(PATHS)]
        c.add(c.line(list(zip(t, W[i])), col, 1.6, glow=False, dur=1.8, begin=0.2 + i * 0.12,
                     flow=True, flow_color=col, flow_dur=3.2 + i * 0.6))
    c.add(_caption(c, "USE: foundation of continuous-time finance"))
    return c.save("sp_brownian.svg")


# ── 2. Geometric Brownian motion ───────────────────────────────────────────────
def gbm():
    rng = np.random.default_rng(2)
    n, steps = 5, 220
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    mu, sig, S0 = 0.14, 0.45, 100.0
    W = np.column_stack([np.zeros(n), np.cumsum(rng.normal(0, math.sqrt(dt), (n, steps)), axis=1)])
    S = S0 * np.exp((mu - 0.5 * sig ** 2) * t + sig * W)

    c = _new("GEOMETRIC BROWNIAN MOTION", "dSₜ = μSₜ dt + σSₜ dWₜ")
    c.set_xlim(0, 1)
    c.set_ylim(S.min() * 0.95, S.max() * 1.05)
    _axes(c, "Sₜ", lambda v: f"{v:.0f}")
    c.add(f'<line x1="{c.x0}" y1="{c.sy(S0):.1f}" x2="{c.x1}" y2="{c.sy(S0):.1f}" stroke="{MUTED}" stroke-dasharray="3 3" stroke-width="1" opacity="0.4"/>')
    for i in range(n):
        col = PATHS[i % len(PATHS)]
        c.add(c.line(list(zip(t, S[i])), col, 1.6, glow=False, dur=1.8, begin=0.2 + i * 0.12,
                     flow=True, flow_color=col, flow_dur=3.2 + i * 0.6))
    c.add(_caption(c, "USE: Black–Scholes · equity & FX prices"))
    return c.save("sp_gbm.svg")


# ── 3. Ornstein–Uhlenbeck (mean reversion) ─────────────────────────────────────
def ou():
    rng = np.random.default_rng(4)
    n, steps = 5, 240
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    theta, mu, sigma = 6.0, 0.0, 0.45
    X = np.zeros((n, steps + 1))
    X[:, 0] = rng.uniform(-1.6, 1.6, n)
    for k in range(steps):
        X[:, k + 1] = X[:, k] + theta * (mu - X[:, k]) * dt + sigma * math.sqrt(dt) * rng.normal(size=n)

    c = _new("ORNSTEIN–UHLENBECK", "dXₜ = θ(μ−Xₜ) dt + σ dWₜ")
    c.set_xlim(0, 1)
    c.set_ylim(X.min() * 1.15, X.max() * 1.15)
    _axes(c, "Xₜ", lambda v: f"{v:+.1f}")
    c.add(f'<line x1="{c.x0}" y1="{c.sy(mu):.1f}" x2="{c.x1}" y2="{c.sy(mu):.1f}" stroke="{GREEN}" stroke-dasharray="4 3" stroke-width="1.2" opacity="0.5"/>')
    c.add(f'<text x="{c.x1 - 4}" y="{c.sy(mu) - 5:.1f}" fill="{GREEN}" font-size="9" text-anchor="end" opacity="0.7">μ (mean)</text>')
    for i in range(n):
        c.add(c.line(list(zip(t, X[i])), PATHS[i % len(PATHS)], 1.5, glow=False, dur=1.9, begin=0.2 + i * 0.12))
    c.add(_caption(c, "USE: rates · pairs / stat-arb · spreads"))
    return c.save("sp_ou.svg")


# ── 4. Cox–Ingersoll–Ross (non-negative rates) ─────────────────────────────────
def cir():
    rng = np.random.default_rng(6)
    n, steps = 5, 240
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    a, b, sigma = 3.0, 0.045, 0.16
    X = np.zeros((n, steps + 1))
    X[:, 0] = rng.uniform(0.012, 0.085, n)
    for k in range(steps):
        x = np.maximum(X[:, k], 0)
        X[:, k + 1] = np.maximum(x + a * (b - x) * dt + sigma * np.sqrt(x * dt) * rng.normal(size=n), 0)
    Xp = X * 100  # to percent

    c = _new("COX–INGERSOLL–ROSS", "drₜ = a(b−rₜ) dt + σ√rₜ dWₜ")
    c.set_xlim(0, 1)
    c.set_ylim(0, Xp.max() * 1.15)
    _axes(c, "rₜ (%)", lambda v: f"{v:.1f}")
    c.add(f'<line x1="{c.x0}" y1="{c.sy(b*100):.1f}" x2="{c.x1}" y2="{c.sy(b*100):.1f}" stroke="{GREEN}" stroke-dasharray="4 3" stroke-width="1.2" opacity="0.5"/>')
    c.add(f'<text x="{c.x1 - 4}" y="{c.sy(b*100) - 5:.1f}" fill="{GREEN}" font-size="9" text-anchor="end" opacity="0.7">b (long-run)</text>')
    for i in range(n):
        c.add(c.line(list(zip(t, Xp[i])), PATHS[i % len(PATHS)], 1.5, glow=False, dur=1.9, begin=0.2 + i * 0.12))
    c.add(_caption(c, "USE: short rates · default intensity λ · vol"))
    return c.save("sp_cir.svg")


# ── 5. Merton jump-diffusion ───────────────────────────────────────────────────
def jump_diffusion():
    rng = np.random.default_rng(8)
    steps = 260
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    mu, sig, S0 = 0.06, 0.18, 100.0
    lam, jm, js = 9.0, -0.07, 0.03  # jumps/yr, jump mean (down), jump std

    c = _new("MERTON JUMP-DIFFUSION", "dSₜ = μ dt + σ dWₜ + dJₜ")
    n = 3
    jump_dots = []
    allS = []
    for p in range(n):
        logS = np.zeros(steps + 1)
        logS[0] = math.log(S0)
        jumps_at = []
        for k in range(steps):
            diff = (mu - 0.5 * sig ** 2) * dt + sig * math.sqrt(dt) * rng.normal()
            njump = rng.poisson(lam * dt)
            jmp = sum(rng.normal(jm, js) for _ in range(njump))
            logS[k + 1] = logS[k] + diff + jmp
            if njump > 0:
                jumps_at.append(k + 1)
        S = np.exp(logS)
        allS.append((S, jumps_at, p))
    Sall = np.concatenate([s for s, _, _ in allS])

    c.set_xlim(0, 1)
    c.set_ylim(Sall.min() * 0.95, Sall.max() * 1.05)
    _axes(c, "Sₜ", lambda v: f"{v:.0f}")
    for S, jumps_at, p in allS:
        color = PATHS[p % len(PATHS)]
        c.add(c.line(list(zip(t, S)), color, 1.6, glow=False, dur=2.0, begin=0.2 + p * 0.15,
                     flow=True, flow_color=color, flow_dur=3.6 + p * 0.7))
        for k in jumps_at:
            jump_dots.append(c.dot(t[k], S[k], RED, r=2.6, begin=2.2, glow=True))
    for d in jump_dots:
        c.add(d)
    c.add(f'<text x="{c.x1 - 4}" y="{c.yt + 12}" fill="{RED}" font-size="9" text-anchor="end" opacity="0">'
          f'<animate attributeName="opacity" to="0.85" dur="0.5s" begin="2.3s" fill="freeze"/>● jump</text>')
    c.add(_caption(c, "USE: crashes · gap risk · default events"))
    return c.save("sp_jump.svg")


# ── 6. Monte-Carlo fan (simulation → distribution) ─────────────────────────────
def monte_carlo():
    rng = np.random.default_rng(10)
    N, steps = 80, 200
    dt = 1 / steps
    t = np.linspace(0, 1, steps + 1)
    mu, sig, S0 = 0.10, 0.35, 100.0
    W = np.column_stack([np.zeros(N), np.cumsum(rng.normal(0, math.sqrt(dt), (N, steps)), axis=1)])
    S = S0 * np.exp((mu - 0.5 * sig ** 2) * t + sig * W)

    med = np.percentile(S, 50, axis=0)
    lo, hi = np.percentile(S, 5, axis=0), np.percentile(S, 95, axis=0)

    c = _new("MONTE-CARLO SIMULATION", "S_T = S₀·exp((μ−½σ²)T + σW_T)")
    c.set_xlim(0, 1)
    c.set_ylim(S.min() * 0.95, S.max() * 1.05)
    _axes(c, "Sₜ", lambda v: f"{v:.0f}")

    # faint cloud of all paths (single grouped fade-in)
    faint = [f'<g stroke="{GREEN}" stroke-width="0.7" fill="none" opacity="0">'
             f'<animate attributeName="opacity" from="0" to="0.16" dur="1.3s" begin="0.3s" fill="freeze"/>']
    for i in range(N):
        d = "M " + " ".join(f"{c.sx(x):.1f} {c.sy(y):.1f}" for x, y in zip(t, S[i]))
        faint.append(f'<path d="{d}"/>')
    faint.append("</g>")
    c.add("".join(faint))

    c.add(c.band(t, lo, hi, CYAN, 0.12, begin=1.4, dur=1.0))
    c.add(c.line(list(zip(t, med)), CYAN, 2.0, dur=1.8, begin=0.4))
    c.add(c.line(list(zip(t, hi)), AMBER, 1.2, glow=False, dur=1.2, begin=1.6, dash="5 3"))
    c.add(c.line(list(zip(t, lo)), AMBER, 1.2, glow=False, dur=1.2, begin=1.6, dash="5 3"))
    c.add(_caption(c, "USE: derivative pricing · VaR · risk-neutral E[·]"))
    return c.save("sp_montecarlo.svg")


def main():
    import os
    # Narrative arc: random walk → asset prices → default events (→ credit)
    for fn in (brownian, gbm, jump_diffusion):
        path = fn()
        print(f"wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    main()
