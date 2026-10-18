"""
Build the README graphics for ORGEE.

Writes light and dark versions of five SVGs into docs/assets/:
    banner    animated customer funnel (500K visits -> 47K purchases)
    receipt   headline business numbers, styled as a till receipt
    verdicts  the five growth ideas tested and whether each held up
    funnel    stage-by-stage drop-off, largest leak highlighted
    abtest    the A/B result: effect, 95% CI and detectable effect

Every number below comes from the phase result documents in this repo.
Pure Python, no dependencies. Run from the repo root:

    python docs/build_readme_assets.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets"

# ---------------------------------------------------------------- numbers
FUNNEL = [  # Phase 5, 04_Funnel_Analysis_Results.md
    ("Visit", 500_000),
    ("Product view", 405_699),
    ("Add to cart", 151_078),
    ("Checkout", 81_736),
    ("Purchase", 47_418),
]
RECEIPT = [  # Phases 4 and 6
    ("Delivered revenue", "R$13.22M"),
    ("Delivered orders", "96,478"),
    ("Active customers", "93,358"),
    ("Average order value", "R$137.04"),
    ("Placed a 2nd order", "3.00%"),
    ("Revenue from top 10%", "41.14%"),
]
AB = dict(  # Phase 8, 05_Statistical_Significance_Results.md
    c_rate=2.16, c_conv=48, c_n=2223,
    t_rate=2.06, t_conv=45, t_n=2188,
    diff=-0.10, lo=-0.95, hi=0.75, p=0.8126, mde=1.23,
)

THEMES = {
    "light": dict(
        paper="#FAF6EF", card="#FFFFFF", ink="#1F1B16", muted="#6B635A",
        rule="#E2D9CB", soft="#EFE8DC", terra="#C2410C", terra_soft="#F6DCCB",
        green="#2F7D4F", green_soft="#D5EBDD", track="#E9E1D4",
    ),
    "dark": dict(
        paper="#15120F", card="#1E1A16", ink="#F3EDE4", muted="#A79E92",
        rule="#3A332C", soft="#26211C", terra="#F08A4B", terra_soft="#4A2A18",
        green="#5DBB82", green_soft="#1F3A2A", track="#2E2822",
    ),
}

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', Consolas, 'Liberation Mono', monospace"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=16, fill="#000", weight=400, anchor="start",
         family=SANS, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>'
            f"{esc(s)}</text>")


def svg(w, h, body, title, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title>"
            + (f"<style>{style}</style>" if style else "")
            + body + "</svg>")


def k(n):
    return f"{n / 1000:.0f}K"


# ---------------------------------------------------------------- banner
def banner(t):
    W, H = 1280, 420
    b = [f'<rect width="{W}" height="{H}" fill="{t["paper"]}"/>']
    # faint ledger lines
    for y in range(40, H, 28):
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{t["soft"]}" stroke-width="1"/>')
    b.append(f'<line x1="44" y1="0" x2="44" y2="{H}" stroke="{t["terra_soft"]}" stroke-width="2"/>')

    b.append(text(72, 92, "O R G E E", 15, t["terra"], 700, family=SANS,
                  extra='letter-spacing="3"'))
    for i, line in enumerate(["Omnichannel Retail &", "Growth Experimentation", "Engine"]):
        b.append(text(72, 146 + i * 50, line, 42, t["ink"], 700, family=SERIF))
    b.append(text(72, 318, "500,000 shopping sessions. Five growth ideas tested.", 18, t["muted"]))
    b.append(text(72, 344, "Three of them didn't hold up, and the data says so.", 18, t["muted"]))

    # funnel columns
    cx0, gap, cw, mid, hmax = 690, 116, 64, 210, 230
    xs, hs = [], []
    for i, (name, v) in enumerate(FUNNEL):
        h = hmax * v / FUNNEL[0][1]
        x = cx0 + i * gap
        xs.append(x)
        hs.append(h)
        fill = t["green"] if i == len(FUNNEL) - 1 else t["ink"]
        b.append(f'<rect x="{x}" y="{mid - h / 2:.1f}" width="{cw}" height="{h:.1f}" '
                 f'rx="4" fill="{fill}" opacity="0.10"/>')
        b.append(f'<rect x="{x}" y="{mid - h / 2:.1f}" width="{cw}" height="{h:.1f}" '
                 f'rx="4" fill="none" stroke="{fill}" stroke-opacity="0.45"/>')
        b.append(text(x + cw / 2, mid - hmax / 2 - 14, k(v), 15, t["ink"], 700, "middle"))
        b.append(text(x + cw / 2, mid + hmax / 2 + 26, name, 13, t["muted"], 400, "middle"))

    # biggest leak callout (product view -> add to cart)
    lx = (xs[1] + cw + xs[2]) / 2
    b.append(f'<path d="M{lx} {mid + 40} V{mid + 160} h14" fill="none" stroke="{t["terra"]}" stroke-width="1.6"/>')
    b.append(text(lx + 20, mid + 165, "62.76% of viewers leave before the cart", 15, t["terra"], 700))

    # animated shoppers: share of 40 dots leaving at each stage
    exits = [8, 20, 6, 3, 3]          # left at visit, view, cart, checkout; purchased
    css = []
    dots = []
    span = (xs[-1] + cw + 30) - (cx0 - 30)
    dur = 7.0
    for e in range(5):
        stop = xs[e] + cw / 2 if e < 4 else xs[-1] + cw + 30
        start_x = cx0 - 30
        travel = (stop - start_x) / span
        t_stop = 4 + travel * 70
        if e < 4:
            css.append(
                f"@keyframes e{e}{{0%{{transform:translate({start_x}px,0);opacity:0}}"
                f"4%{{opacity:.9}}{t_stop:.1f}%{{transform:translate({stop:.0f}px,0);opacity:.9}}"
                f"{t_stop + 14:.1f}%{{transform:translate({stop + 14:.0f}px,70px);opacity:0}}"
                f"100%{{transform:translate({stop + 14:.0f}px,70px);opacity:0}}}}")
        else:
            css.append(
                f"@keyframes e4{{0%{{transform:translate({start_x}px,0);opacity:0}}"
                f"4%{{opacity:.9}}{t_stop:.1f}%{{transform:translate({stop:.0f}px,0);opacity:1}}"
                f"{t_stop + 8:.1f}%{{transform:translate({stop + 10:.0f}px,0);opacity:0}}"
                f"100%{{opacity:0}}}}")
    n = 0
    for e, count in enumerate(exits):
        half = hs[e] / 2 - 6
        for j in range(count):
            y = mid - half + 2 * half * ((j * 0.618 + e * 0.37) % 1)
            delay = (n * 0.173) % dur
            color = t["green"] if e == 4 else (t["terra"] if e == 1 else t["ink"])
            dots.append(f'<circle class="d" cx="0" cy="{y:.1f}" r="3.2" fill="{color}" '
                        f'style="animation:e{e} {dur}s linear {delay:.2f}s infinite"/>')
            n += 1
    css.append(".d{opacity:0}")
    css.append("@media (prefers-reduced-motion: reduce){.d{animation:none!important;opacity:0}}")
    b.extend(dots)
    return svg(W, H, "".join(b),
               "ORGEE: 500,000 sessions flow through the funnel to 47,418 purchases; "
               "62.76% leave between product view and add to cart.",
               "".join(css))


# ---------------------------------------------------------------- receipt
def receipt(t):
    W, H = 400, 610
    b = []
    zig = " ".join(f"L{x} {H - 22 + (10 if i % 2 else 0)}"
                   for i, x in enumerate(range(W - 16, 15, -12)))
    b.append(f'<path d="M16 14 H{W - 16} V{H - 22} {zig} L16 14 Z" '
             f'fill="{t["card"]}" stroke="{t["rule"]}"/>')
    y = 58
    b.append(text(W / 2, y, "ORGEE MARKETPLACE", 18, t["ink"], 700, "middle", MONO))
    y += 24
    b.append(text(W / 2, y, "Olist · Brazil · 2016-2018", 13, t["muted"], 400, "middle", MONO))
    y += 26

    def dashes(yy):
        return f'<line x1="36" y1="{yy}" x2="{W - 36}" y2="{yy}" stroke="{t["muted"]}" stroke-dasharray="4 5" stroke-opacity=".6"/>'

    b.append(dashes(y))
    y += 34
    for label, val in RECEIPT:
        b.append(text(36, y, label, 14, t["ink"], 400, family=MONO))
        b.append(text(W - 36, y, val, 14, t["ink"], 700, "end", MONO))
        y += 30
    b.append(dashes(y - 10))
    y += 22
    for label, val in [("Shopping sessions", "500,000"), ("Ended in a purchase", "9.48%")]:
        b.append(text(36, y, label, 14, t["ink"], 400, family=MONO))
        b.append(text(W - 36, y, val, 14, t["ink"], 700, "end", MONO))
        y += 30
    b.append(dashes(y - 10))
    y += 26
    b.append(text(36, y, "GROWTH IDEAS TESTED", 15, t["ink"], 700, family=MONO))
    b.append(text(W - 36, y, "5", 15, t["ink"], 700, "end", MONO))
    y += 26
    b.append(text(36, y, "held up", 14, t["green"], 700, family=MONO))
    b.append(text(W - 36, y, "2", 14, t["green"], 700, "end", MONO))
    y += 24
    b.append(text(36, y, "didn't hold up", 14, t["terra"], 700, family=MONO))
    b.append(text(W - 36, y, "3", 14, t["terra"], 700, "end", MONO))
    y += 30
    # barcode
    x = 92
    widths = [2, 1, 3, 1, 2, 2, 1, 3, 1, 1, 2, 3, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 1, 2, 3, 1, 1, 2, 1, 3, 2]
    for i, wv in enumerate(widths):
        if i % 2 == 0:
            b.append(f'<rect x="{x}" y="{y}" width="{wv * 2}" height="34" fill="{t["ink"]}"/>')
        x += wv * 2 + 2
    y += 52
    b.append(text(W / 2, y, "values in Brazilian reais (R$)", 12, t["muted"], 400, "middle", MONO))
    return svg(W, H, "".join(b),
               "Receipt of headline numbers: R$13.22M delivered revenue, 96,478 orders, "
               "93,358 customers, R$137.04 average order, 3.00% repeat rate, top 10% of "
               "customers bring 41.14% of revenue; 5 growth ideas tested, 2 held up, 3 did not.")


# ---------------------------------------------------------------- verdicts
VERDICTS = [
    dict(claim="Personalized picks beat best-sellers",
         ev="Hit Rate@5: engine 0.07% vs popularity baseline 1.07%",
         ok=False, bars=[("Engine", 0.07), ("Best-sellers", 1.07)], vmax=1.2, unit="%"),
    dict(claim="Personalization lifts conversion (A/B test)",
         ev="2.06% vs 2.16% control, p = 0.81 → DO NOT SHIP",
         ok=False, bars=[("Treatment", 2.06), ("Control", 2.16)], vmax=2.5, unit="%"),
    dict(claim="Some marketing channels work better",
         ev="All 5 channels convert at 0.78% to 0.83%, within 0.05 pts",
         ok=False, bars=[("Display", 0.83), ("Search", 0.81), ("Social", 0.80),
                         ("Email", 0.80), ("Push", 0.78)], vmax=1.0, unit="%", tiny=True),
    dict(claim="A small group of customers drives revenue",
         ev="Top 10% of customers bring 41.14% of revenue",
         ok=True, bars=[("Top 10%", 41.14), ("Other 90%", 58.86)], vmax=70, unit="%"),
    dict(claim="Retention is the weakest link",
         ev="Only 0.48% return in month one; 3.00% ever reorder",
         ok=True, bars=[("Month 0", 100), ("Month 1", 0.48)], vmax=110, unit="%"),
]


def verdicts(t):
    W, row = 1200, 104
    H = 92 + row * len(VERDICTS) + 20
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{t["paper"]}" stroke="{t["rule"]}"/>']
    b.append(text(40, 52, "Five growth ideas, tested against the data", 24, t["ink"], 700, family=SERIF))
    b.append(text(W - 40, 52, "2 held up · 3 didn't", 15, t["muted"], 400, "end"))
    for i, v in enumerate(VERDICTS):
        y0 = 84 + i * row
        b.append(f'<rect x="24" y="{y0}" width="{W - 48}" height="{row - 12}" rx="10" fill="{t["card"]}" stroke="{t["rule"]}"/>')
        b.append(text(52, y0 + 38, f"{i + 1:02d}", 15, t["muted"], 700, family=MONO))
        b.append(text(96, y0 + 38, v["claim"], 19, t["ink"], 700, family=SERIF))
        b.append(text(96, y0 + 66, v["ev"], 14, t["muted"]))
        # mini bars
        bx, bw = 640, 250
        n = len(v["bars"])
        bh = 8 if v.get("tiny") else 12
        step = (row - 30) / n
        for j, (lab, val) in enumerate(v["bars"]):
            yy = y0 + 14 + j * step + (step - bh) / 2
            b.append(f'<rect x="{bx + 84}" y="{yy:.1f}" width="{bw - 84}" height="{bh}" rx="{bh / 2}" fill="{t["track"]}"/>')
            wv = max((bw - 84) * val / v["vmax"], 2)
            col = t["muted"] if v.get("tiny") else (t["green"] if v["ok"] and j == 0 else (t["terra"] if (not v["ok"] and j == 0) else t["muted"]))
            b.append(f'<rect x="{bx + 84}" y="{yy:.1f}" width="{wv:.1f}" height="{bh}" rx="{bh / 2}" fill="{col}"/>')
            if not v.get("tiny"):
                b.append(text(bx + 76, yy + bh - 1, lab, 12, t["muted"], 400, "end"))
        # stamp
        sx, sy = W - 196, y0 + 22
        col = t["green"] if v["ok"] else t["terra"]
        word = "HELD UP" if v["ok"] else "DIDN'T HOLD"
        b.append(f'<g transform="rotate(-4 {sx + 74} {sy + 24})">'
                 f'<rect x="{sx}" y="{sy}" width="148" height="46" rx="6" fill="none" stroke="{col}" stroke-width="2.4"/>'
                 f'<rect x="{sx + 4}" y="{sy + 4}" width="140" height="38" rx="4" fill="none" stroke="{col}" stroke-width="1" stroke-opacity=".6"/>'
                 + text(sx + 74, sy + 30, word, 16, col, 800, "middle", SANS, 'letter-spacing="1.5"')
                 + "</g>")
    return svg(W, H, "".join(b),
               "Five growth ideas tested: personalized recommendations, A/B personalization "
               "and channel differences did not hold up; revenue concentration and weak "
               "retention held up.")


# ---------------------------------------------------------------- funnel
def funnel(t):
    W, H = 1000, 330
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{t["paper"]}" stroke="{t["rule"]}"/>']
    b.append(text(36, 46, "Where 500,000 shopping sessions go", 21, t["ink"], 700, family=SERIF))
    x0, wmax, rh = 190, 560, 44
    prev = None
    for i, (name, v) in enumerate(FUNNEL):
        y = 74 + i * rh
        w = wmax * v / FUNNEL[0][1]
        last = i == len(FUNNEL) - 1
        b.append(text(x0 - 16, y + 23, name, 15, t["ink"], 400, "end"))
        b.append(f'<rect x="{x0}" y="{y + 6}" width="{w:.1f}" height="26" rx="4" '
                 f'fill="{t["green"] if last else t["ink"]}" opacity="{1 if last else 0.82}"/>')
        b.append(text(x0 + w + 10, y + 24, f"{v:,}", 14, t["ink"], 700))
        if prev:
            drop = 100 * (1 - v / prev)
            big = name == "Add to cart"
            b.append(text(W - 36, y + 4, f"−{drop:.2f}%", 15 if big else 13,
                          t["terra"] if big else t["muted"], 700 if big else 400, "end"))
            if big:
                b.append(text(W - 36, y + 22, "biggest leak", 12, t["terra"], 400, "end"))
        prev = v
    b.append(text(x0, H - 16, "9.48% of sessions end in a purchase. Right column: share lost from the stage above.",
                  13, t["muted"]))
    return svg(W, H, "".join(b),
               "Funnel: 500,000 visits, 405,699 product views, 151,078 add to cart, 81,736 "
               "checkouts, 47,418 purchases; the largest drop is 62.76% before add to cart.")


# ---------------------------------------------------------------- A/B test
def abtest(t):
    W, H = 1000, 300
    a = AB
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="{t["paper"]}" stroke="{t["rule"]}"/>']
    b.append(text(36, 46, "Did personalized recommendations lift conversion?", 21, t["ink"], 700, family=SERIF))
    b.append(text(36, 72, f"Control {a['c_rate']:.2f}% ({a['c_conv']} of {a['c_n']:,})   ·   "
                          f"Treatment {a['t_rate']:.2f}% ({a['t_conv']} of {a['t_n']:,})", 14, t["muted"]))
    lo, hi = -1.6, 1.6
    x0, x1, yax = 120, 880, 170

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    # detectable region
    b.append(f'<rect x="{X(a["mde"]):.1f}" y="{yax - 52}" width="{X(hi) - X(a["mde"]):.1f}" height="104" fill="{t["green_soft"]}"/>')
    b.append(text(X(a["mde"]) + 8, yax - 34, "lifts this test", 12, t["green"], 700))
    b.append(text(X(a["mde"]) + 8, yax - 19, "could reliably detect", 12, t["green"], 700))
    b.append(f'<line x1="{X(a["mde"]):.1f}" y1="{yax - 52}" x2="{X(a["mde"]):.1f}" y2="{yax + 52}" stroke="{t["green"]}" stroke-dasharray="4 4"/>')
    # axis
    b.append(f'<line x1="{x0}" y1="{yax + 40}" x2="{x1}" y2="{yax + 40}" stroke="{t["rule"]}"/>')
    for v in [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]:
        b.append(f'<line x1="{X(v):.1f}" y1="{yax + 40}" x2="{X(v):.1f}" y2="{yax + 46}" stroke="{t["muted"]}"/>')
        b.append(text(X(v), yax + 64, f"{v:+.1f}" if v else "0", 12, t["muted"], 400, "middle"))
    b.append(f'<line x1="{X(0):.1f}" y1="{yax - 52}" x2="{X(0):.1f}" y2="{yax + 40}" stroke="{t["ink"]}" stroke-width="1.4"/>')
    b.append(text(X(0), yax - 58, "no effect", 12, t["ink"], 400, "middle"))
    # CI
    b.append(f'<line x1="{X(a["lo"]):.1f}" y1="{yax}" x2="{X(a["hi"]):.1f}" y2="{yax}" stroke="{t["terra"]}" stroke-width="4" stroke-linecap="round"/>')
    for v in (a["lo"], a["hi"]):
        b.append(f'<line x1="{X(v):.1f}" y1="{yax - 10}" x2="{X(v):.1f}" y2="{yax + 10}" stroke="{t["terra"]}" stroke-width="2.4"/>')
    b.append(f'<circle cx="{X(a["diff"]):.1f}" cy="{yax}" r="8" fill="{t["terra"]}" stroke="{t["paper"]}" stroke-width="2"/>')
    b.append(text(X(a["diff"]) - 12, yax - 16, f"{a['diff']:+.2f} pts", 13, t["terra"], 700, "end"))
    b.append(text(X(a["lo"]), yax - 16, f"{a['lo']:+.2f}", 12, t["terra"], 400, "middle"))
    b.append(text(X(a["hi"]), yax - 16, f"{a['hi']:+.2f}", 12, t["terra"], 400, "middle"))
    b.append(text(36, H - 18,
                  f"Treatment minus control in percentage points, with 95% CI. p = {a['p']}: not significant. "
                  f"Only lifts of +{a['mde']} pts or more were reliably detectable.",
                  13, t["muted"]))
    return svg(W, H, "".join(b),
               "A/B test: treatment minus control is -0.10 points, 95% CI -0.95 to +0.75, "
               "p = 0.8126; the test could reliably detect only lifts of +1.23 points or more.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("banner", banner), ("receipt", receipt), ("verdicts", verdicts),
                     ("funnel", funnel), ("abtest", abtest)]:
        for theme, t in THEMES.items():
            p = OUT / f"{name}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print("wrote", p.relative_to(OUT.parent.parent))


if __name__ == "__main__":
    main()
