"""Tiny SVG charting toolkit shared by the chart generators.

Hand-built animated (SMIL) SVG: draw-on lines, growing bars, fading/breathing
bands, looping flow dots and a sweeping scanner. Everything animates natively on
GitHub (no JavaScript), the same mechanism that scrolls ticker.svg.

Exposes a dark terminal theme, a few helpers (esc, nice_ticks, heat_color) and
the `Chart` class. Charts are written to ./charts/.
"""
import math
import os

import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")

# ── Theme (matches ticker.svg) ─────────────────────────────────────────────────
BG    = "#0d1117"
GREEN = "#00ff41"
RED   = "#ff4d4d"
AMBER = "#ffb000"
CYAN  = "#00d4ff"
GRID  = "#1b2430"
MUTED = "#8b949e"
FONT  = "ui-monospace, SFMono-Regular, monospace"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nice_ticks(lo, hi, n=5):
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = mag * 10
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    start = math.ceil(lo / step) * step
    out, v = [], start
    while v <= hi + step * 1e-6:
        out.append(round(v, 10))
        v += step
    return out


def lerp_color(c0, c1, f):
    return tuple(int(round(a + (b - a) * f)) for a, b in zip(c0, c1))


def heat_color(t):
    """t in [0,1] → green → amber → red."""
    t = max(0.0, min(1.0, t))
    stops = [(0.0, (0, 255, 65)), (0.5, (255, 176, 0)), (1.0, (255, 77, 77))]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            r, g, b = lerp_color(c0, c1, f)
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#ff4d4d"


# ── SVG chart canvas ───────────────────────────────────────────────────────────
class Chart:
    def __init__(self, title="", subtitle="", width=560, height=340,
                 pad=(56, 22, 48, 66)):
        self.w, self.h = width, height
        self.pt, self.pr, self.pb, self.pl = pad   # top, right, bottom, left
        self.title, self.subtitle = title, subtitle
        self.body = []
        self.xlim = (0, 1)
        self.ylim = (0, 1)
        self._uid = 0

    def _id(self):
        self._uid += 1
        return f"p{self._uid}"

    # plot-area pixel bounds
    @property
    def x0(self): return self.pl
    @property
    def x1(self): return self.w - self.pr
    @property
    def yb(self): return self.h - self.pb   # bottom (ymin)
    @property
    def yt(self): return self.pt             # top (ymax)

    def set_xlim(self, a, b): self.xlim = (a, b)
    def set_ylim(self, a, b): self.ylim = (a, b)

    def sx(self, x):
        a, b = self.xlim
        return self.x0 + (x - a) / (b - a) * (self.x1 - self.x0)

    def sy(self, y):
        a, b = self.ylim
        return self.yb + (y - a) / (b - a) * (self.yt - self.yb)

    def add(self, s):
        self.body.append(s)

    # ── building blocks ────────────────────────────────────────────────────────
    def grid_axes(self, xticks, yticks, xfmt=str, yfmt=str, xlabel="", ylabel=""):
        out = []
        for yv in yticks:
            py = self.sy(yv)
            out.append(f'<line x1="{self.x0}" y1="{py:.1f}" x2="{self.x1}" y2="{py:.1f}" stroke="{GRID}" stroke-width="1"/>')
            out.append(f'<text x="{self.x0 - 8}" y="{py + 3:.1f}" fill="{MUTED}" font-size="9" text-anchor="end">{esc(yfmt(yv))}</text>')
        for xv in xticks:
            px = self.sx(xv)
            out.append(f'<line x1="{px:.1f}" y1="{self.yt}" x2="{px:.1f}" y2="{self.yb}" stroke="{GRID}" stroke-width="1"/>')
            out.append(f'<text x="{px:.1f}" y="{self.yb + 15:.1f}" fill="{MUTED}" font-size="9" text-anchor="middle">{esc(xfmt(xv))}</text>')
        if xlabel:
            out.append(f'<text x="{(self.x0 + self.x1) / 2:.1f}" y="{self.h - 8}" fill="{MUTED}" font-size="10" text-anchor="middle">{esc(xlabel)}</text>')
        if ylabel:
            cy = (self.yt + self.yb) / 2
            out.append(f'<text transform="translate(15,{cy:.1f}) rotate(-90)" fill="{MUTED}" font-size="10" text-anchor="middle">{esc(ylabel)}</text>')
        self.body = out + self.body

    def line(self, pts, color, width=2, glow=True, dur=1.6, begin=0.0, dash=None,
             flow=False, flow_dur=3.6, flow_color=None):
        d = "M " + " L ".join(f"{self.sx(x):.1f} {self.sy(y):.1f}" for x, y in pts)
        filt = ' filter="url(#glow)"' if glow else ""
        pid = self._id()
        if dash:
            # dashed lines: reveal via opacity instead of dashoffset (dash already used)
            path = (f'<path id="{pid}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{filt} '
                    f'stroke-dasharray="{dash}" opacity="0">'
                    f'<animate attributeName="opacity" from="0" to="1" dur="{dur}s" begin="{begin}s" fill="freeze"/></path>')
        else:
            path = (f'<path id="{pid}" d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{filt} '
                    f'stroke-dasharray="1" pathLength="1" stroke-dashoffset="1">'
                    f'<animate attributeName="stroke-dashoffset" from="1" to="0" dur="{dur}s" begin="{begin}s" fill="freeze" '
                    f'calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1"/></path>')
        if flow:
            fc = flow_color or "#ffffff"
            path += (f'<circle r="3" fill="{fc}" filter="url(#glow)" opacity="0">'
                     f'<animate attributeName="opacity" to="0.95" dur="0.3s" begin="{begin + dur}s" fill="freeze"/>'
                     f'<animateMotion dur="{flow_dur}s" begin="{begin + dur}s" repeatCount="indefinite" '
                     f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"><mpath href="#{pid}"/></animateMotion></circle>')
        return path

    def band(self, xs, lo, hi, fill, opacity, begin=0.0, dur=0.8, breathe=False):
        top = " ".join(f"{self.sx(x):.1f} {self.sy(y):.1f}" for x, y in zip(xs, hi))
        bot = " ".join(f"{self.sx(x):.1f} {self.sy(y):.1f}" for x, y in zip(xs[::-1], lo[::-1]))
        d = f"M {top} {bot} Z"
        anims = (f'<animate attributeName="opacity" from="0" to="{opacity}" dur="{dur}s" begin="{begin}s" fill="freeze"/>')
        if breathe:
            hi_op = min(1.0, opacity * 1.7)
            anims += (f'<animate attributeName="opacity" values="{opacity};{hi_op};{opacity}" dur="4.5s" '
                      f'begin="{begin + dur + 0.2}s" repeatCount="indefinite"/>')
        return f'<path d="{d}" fill="{fill}" stroke="none" opacity="0">{anims}</path>'

    def bar(self, xpx, wpx, ytop, ybase, fill, begin=0.0, dur=0.7, opacity=1.0):
        hgt = ybase - ytop
        spline = 'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.7 0.2 1"'
        return (f'<rect x="{xpx:.1f}" y="{ybase:.1f}" width="{wpx:.1f}" height="0" rx="1.5" fill="{fill}" opacity="{opacity}">'
                f'<animate attributeName="y" to="{ytop:.1f}" dur="{dur}s" begin="{begin}s" fill="freeze" {spline}/>'
                f'<animate attributeName="height" to="{hgt:.1f}" dur="{dur}s" begin="{begin}s" fill="freeze" {spline}/></rect>')

    def vline(self, xv, color, begin=1.3, dash="4 3", pulse=True):
        px = self.sx(xv)
        pulse_anim = (f'<animate attributeName="stroke-opacity" values="0.55;1;0.55" dur="2.4s" '
                      f'begin="{begin + 0.5}s" repeatCount="indefinite"/>') if pulse else ""
        return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}s" fill="freeze"/>'
                f'<line x1="{px:.1f}" y1="{self.yt}" x2="{px:.1f}" y2="{self.yb}" stroke="{color}" '
                f'stroke-width="1.5" stroke-dasharray="{dash}">{pulse_anim}</line></g>')

    def readout(self, items, x, y, anchor="end", begin=1.8):
        rows = "".join(
            f'<text x="{x}" y="{y + i * 14:.1f}" fill="{color}" text-anchor="{anchor}">{esc(text)}</text>'
            for i, (color, text) in enumerate(items)
        )
        return (f'<g font-size="10" font-weight="bold" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="{begin}s" fill="freeze"/>{rows}</g>')

    def dot(self, x, y, color, r=3.2, begin=0.0, glow=True):
        filt = ' filter="url(#glow)"' if glow else ""
        return (f'<circle cx="{self.sx(x):.1f}" cy="{self.sy(y):.1f}" r="0" fill="{color}"{filt}>'
                f'<animate attributeName="r" to="{r}" dur="0.4s" begin="{begin}s" fill="freeze"/></circle>')

    def tag(self, x, y, text, color, anchor="start", dy=0, begin=0.0):
        return (f'<text x="{self.sx(x) + (5 if anchor == "start" else -5):.1f}" y="{self.sy(y) + dy:.1f}" '
                f'fill="{color}" font-size="10" font-weight="bold" text-anchor="{anchor}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin}s" fill="freeze"/>{esc(text)}</text>')

    def legend(self, items, x, y):
        out = ['<g font-size="9">']
        cy = y
        for color, label in items:
            out.append(f'<rect x="{x}" y="{cy - 7}" width="10" height="10" rx="2" fill="{color}"/>')
            out.append(f'<text x="{x + 15}" y="{cy + 2}" fill="{MUTED}">{esc(label)}</text>')
            cy += 16
        out.append("</g>")
        return "".join(out)

    def render(self):
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
             f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">']
        p.append(
            '<defs>'
            '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
            '<feGaussianBlur stdDeviation="1.6" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
            '</filter></defs>'
        )
        p.append(f'<rect width="{self.w}" height="{self.h}" rx="7" fill="{BG}"/>')
        p.append(f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="7" '
                 f'fill="none" stroke="{GREEN}" stroke-opacity="0.30"/>')
        p.append(f'<text x="{self.pl}" y="28" fill="{GREEN}" font-size="14" font-weight="bold">{esc(self.title)}</text>')
        if self.subtitle:
            p.append(f'<text x="{self.x1}" y="28" fill="{MUTED}" font-size="9.5" text-anchor="end">{esc(self.subtitle)}</text>')
        # live/synthetic blinking indicator
        p.append(f'<circle cx="{self.pl - 12}" cy="24" r="3" fill="{GREEN}" filter="url(#glow)">'
                 f'<animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/></circle>')
        p.extend(self.body)
        p.append("</svg>")
        return "\n".join(p)

    def save(self, name):
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render())
        return path
