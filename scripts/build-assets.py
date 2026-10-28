#!/usr/bin/env python3
"""Generate the monochrome SVG assets used in README.md.

Every asset is written twice (light + dark) so README can swap them with
<picture> and prefers-color-scheme. Edit the content below, then run:

    python3 scripts/build-assets.py
"""
import hashlib
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

HANDLE = "svviitzerland"
NAME = ("FARHAN", "AULIANDA")
TAGLINE = "FULL-STACK  /  AI AGENTS  /  CLOUD"

STACK = [
    ("LANGUAGES", "JavaScript   TypeScript   Python   C#   PHP   C++   Bash"),
    ("FRONTEND", "React   Next.js   Vite"),
    ("BACKEND", "Node.js   Bun   FastAPI   Django   Laravel"),
    ("DATA", "Supabase   PostgreSQL   MySQL   MongoDB   SQLite   Redis"),
    ("AI", "LangChain   Strands Agents"),
    ("INFRA", "Docker   Kubernetes   AWS   GCP   Azure   DigitalOcean   Cloudflare"),
    ("SYSTEM", "Arch Linux"),
]

THEMES = {
    "light": {"ink": "#0A0A0A", "mid": "#6E6E6E", "faint": "#A0A0A0", "hair": "#D0D7DE"},
    "dark": {"ink": "#F0F0F0", "mid": "#8B949E", "faint": "#6E7681", "hair": "#30363D"},
}

SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
W = 1200


def svg(h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="{title}">\n'
        f"<title>{title}</title>\n{body}\n</svg>\n"
    )


def mono(x, y, text, fill, size=13, anchor="start", spacing=2.4):
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'letter-spacing="{spacing}" fill="{fill}" text-anchor="{anchor}">{text}</text>'
    )


def halftone_sphere(cx, cy, r, step, fill, invert=False):
    """Dot-screen shaded sphere, lit from the upper left.

    On a dark background the dots are the light, so the screen is inverted.
    """
    lx, ly, lz = -0.55, -0.6, 0.58
    norm = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / norm, ly / norm, lz / norm
    dots = []
    n = int(r / step) + 1
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            # offset every other row, like a real print screen
            x = i * step + (step / 2 if j % 2 else 0)
            y = j * step * 0.866
            d = math.hypot(x, y)
            if d > r:
                continue
            nx, ny = x / r, y / r
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            light = max(0.0, nx * lx + ny * ly + nz * lz)
            shade = light if invert else 1 - light
            dr = step * 0.5 * (0.12 + 0.88 * shade ** 1.15)
            if dr < 0.45:
                continue
            dots.append(f'<circle cx="{cx + x:.1f}" cy="{cy + y:.1f}" r="{dr:.2f}"/>')
    return f'<g fill="{fill}">' + "".join(dots) + "</g>"


def header(t):
    h = 380
    split = 820
    body = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{t["hair"]}"/>',
        f'<line x1="0" y1="64" x2="{W}" y2="64" stroke="{t["hair"]}"/>',
        f'<line x1="0" y1="{h - 64}" x2="{W}" y2="{h - 64}" stroke="{t["hair"]}"/>',
        f'<line x1="{split}" y1="64" x2="{split}" y2="{h - 64}" stroke="{t["hair"]}"/>',
        mono(40, 38, f"@{HANDLE.upper()}", t["ink"]),
        mono(W - 40, 38, "README.MD  /  PROFILE", t["mid"], anchor="end"),
        f'<text x="36" y="182" font-family="{SANS}" font-weight="700" font-size="112" '
        f'letter-spacing="-3" fill="{t["ink"]}" textLength="560" lengthAdjust="spacingAndGlyphs">{NAME[0]}</text>',
        f'<text x="36" y="290" font-family="{SANS}" font-weight="700" font-size="112" '
        f'letter-spacing="-3" fill="{t["ink"]}" textLength="740" lengthAdjust="spacingAndGlyphs">{NAME[1]}</text>',
        halftone_sphere(1010, 190, 104, 7, t["ink"], invert=t is THEMES["dark"]),
        f'<circle cx="1010" cy="190" r="118" fill="none" stroke="{t["hair"]}"/>',
        f'<line x1="880" y1="190" x2="1140" y2="190" stroke="{t["hair"]}" stroke-dasharray="2 4"/>',
        f'<line x1="1010" y1="78" x2="1010" y2="302" stroke="{t["hair"]}" stroke-dasharray="2 4"/>',
        mono(40, h - 26, TAGLINE, t["ink"]),
        mono(W - 40, h - 26, "BUILDING  VESSAIL.APP", t["mid"], anchor="end"),
    ]
    # registration marks in the corners, a nod to print proofs
    for x, y in ((14, 14), (W - 14, 14), (14, h - 14), (W - 14, h - 14)):
        body.append(
            f'<g stroke="{t["mid"]}"><line x1="{x - 5}" y1="{y}" x2="{x + 5}" y2="{y}"/>'
            f'<line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}"/></g>'
        )
    return svg(h, "\n".join(body), "Farhan Aulianda")


def divider(t):
    h = 24
    ticks = []
    for x in range(0, W + 1, 20):
        th = 10 if x % 200 == 0 else (6 if x % 100 == 0 else 3)
        ticks.append(f'<line x1="{x + 0.5}" y1="{h - th}" x2="{x + 0.5}" y2="{h}"/>')
    body = f'<g stroke="{t["mid"]}">' + "".join(ticks) + "</g>" + (
        f'<line x1="0" y1="{h - 0.5}" x2="{W}" y2="{h - 0.5}" stroke="{t["ink"]}"/>'
    )
    return svg(h, body, "divider")


def stack(t):
    row = 54
    top = 8
    h = top + row * len(STACK) + 8
    body = [f'<line x1="0" y1="{top + 0.5}" x2="{W}" y2="{top + 0.5}" stroke="{t["ink"]}"/>']
    for idx, (label, items) in enumerate(STACK):
        y = top + row * idx
        base = y + 34
        body.append(mono(0, base, f"{idx + 1:02d}", t["faint"], size=12, spacing=1))
        body.append(mono(48, base, label, t["mid"], size=12))
        body.append(
            f'<text x="250" y="{base + 1}" font-family="{SANS}" font-size="20" '
            f'fill="{t["ink"]}" xml:space="preserve">{items}</text>'
        )
        line = t["ink"] if idx == len(STACK) - 1 else t["hair"]
        body.append(f'<line x1="0" y1="{y + row + 0.5}" x2="{W}" y2="{y + row + 0.5}" stroke="{line}"/>')
    return svg(h, "\n".join(body), "Tech stack")


def barcode(t):
    """Decorative barcode seeded from the handle, so it never changes."""
    h = 88
    bits = "".join(f"{b:08b}" for b in hashlib.sha256(HANDLE.encode()).digest())
    bars, x, i = [], 0, 0
    while x < 860:
        wdt = 1 + int(bits[i % len(bits)]) + int(bits[(i + 7) % len(bits)]) * 2
        if i % 2 == 0:
            bars.append(f'<rect x="{x}" y="0" width="{wdt}" height="56"/>')
        x += wdt + (1 if i % 3 else 2)
        i += 1
    body = [
        f'<g fill="{t["ink"]}" transform="translate(170 0)">' + "".join(bars) + "</g>",
        mono(W / 2, 82, "  ".join(HANDLE.upper()), t["mid"], size=12, anchor="middle", spacing=1),
    ]
    return svg(h, "\n".join(body), "end of page")


def main():
    OUT.mkdir(exist_ok=True)
    for name, build in {"header": header, "divider": divider, "stack": stack, "footer": barcode}.items():
        for theme, palette in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(build(palette))
            print(f"assets/{name}-{theme}.svg")


if __name__ == "__main__":
    main()
