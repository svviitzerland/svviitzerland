#!/usr/bin/env python3
"""Generate the monochrome SVG assets used in README.md.

Every asset is written twice (light + dark) so README can swap them with
<picture> and prefers-color-scheme. Animations are plain CSS/SMIL inside the
SVG, which GitHub renders in <img>. Edit the content below, then run:

    python3 scripts/build-assets.py
"""
import hashlib
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

HANDLE = "svviitzerland"
NAME = ("FARHAN", "AULIANDA")
TAGLINE = "FULL-STACK  /  CLOUD  /  AI AGENTS"
NIMBUS_URL = "nimbus.farhanaulianda.my.id"

STACK = [
    ("LANGUAGES", "TypeScript   JavaScript   Python   Go   Rust   Swift   PHP   C#   Bash"),
    ("FRONTEND", "Svelte   SvelteKit   React   Next.js   Vue   Tailwind CSS   Vite"),
    ("BACKEND", "Bun   Node.js   FastAPI   Django   Laravel   Fiber"),
    ("DATA", "Supabase   PostgreSQL   MySQL   MongoDB   SQLite   Redis"),
    ("AI / QUANTUM", "LangChain   Strands Agents   MCP   Qiskit"),
    ("CLOUD", "AWS   Cloudflare Workers   GCP   Azure   Terraform"),
    ("OPS", "Docker   Kubernetes   GitHub Actions   Arch Linux   Neovim"),
]

# (prompt shown, text, is_command)
TERMINAL = [
    (True, "whoami"),
    (False, "farhan aulianda  //  full-stack · cloud · ai agents"),
    (True, "cd ~/nimbus && bun run dev"),
    (False, "[ok] learn cloud computing by playing"),
    (True, f"open https://{NIMBUS_URL}"),
    (False, "[ok] bilingual · no sign-up · phone or laptop"),
]

THEMES = {
    "light": {
        "ink": "#0A0A0A", "mid": "#6E6E6E", "faint": "#A0A0A0", "hair": "#D0D7DE",
        "panel": "#F6F8FA",
        # hooded hacker palette
        "cloth": "#161616", "rim": "#5A5A5A", "void": "#000000", "eye": "#FFFFFF",
        "lid": "#E4E4E4", "logo": "#0A0A0A", "hand": "#9A9A9A", "glow": "#7A7A7A",
    },
    "dark": {
        "ink": "#F0F0F0", "mid": "#8B949E", "faint": "#6E7681", "hair": "#30363D",
        "panel": "#010409",
        "cloth": "#2D333B", "rim": "#6E7681", "void": "#000000", "eye": "#FFFFFF",
        "lid": "#D0D7DE", "logo": "#0D1117", "hand": "#8B949E", "glow": "#6E7681",
    },
}

SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
W = 1200


def svg(h, body, title, style=""):
    css = f"<style>{style}</style>\n" if style else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="{title}">\n'
        f"<title>{title}</title>\n{css}{body}\n</svg>\n"
    )


def mono(x, y, text, fill, size=13, anchor="start", spacing=2.4, extra=""):
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'letter-spacing="{spacing}" fill="{fill}" text-anchor="{anchor}"{extra}>{text}</text>'
    )


def pct(v):
    return f"{v * 100:.3f}%"


def corner_marks(t, h):
    marks = []
    for x, y in ((14, 14), (W - 14, 14), (14, h - 14), (W - 14, h - 14)):
        marks.append(
            f'<g stroke="{t["mid"]}"><line x1="{x - 5}" y1="{y}" x2="{x + 5}" y2="{y}"/>'
            f'<line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}"/></g>'
        )
    return "".join(marks)


# ---------------------------------------------------------------- globe ----

def globe(cx, cy, r, t, period=24.0, steps=36):
    """Dot globe spinning on its axis, seen from slightly above.

    Every latitude ring gets one keyframe track; the dots on that ring share it
    and are spread around the orbit with negative animation delays. Dots on the
    far side shrink and fade, which reads as halftone shading.
    """
    tilt = math.radians(22)
    css, dots = [], []
    for ring, lat_deg in enumerate(range(-72, 73, 12)):
        lat = math.radians(lat_deg)
        a = r * math.cos(lat)
        y0 = cy - r * math.sin(lat) * math.cos(tilt)
        frames = []
        for s in range(steps + 1):
            th = 2 * math.pi * s / steps
            x = cx + a * math.sin(th)
            y = y0 + a * math.sin(tilt) * math.cos(th)
            z = math.cos(lat) * math.cos(th) * math.cos(tilt) + math.sin(lat) * math.sin(tilt)
            k = (z + 1) / 2
            frames.append(
                f"{pct(s / steps)}{{transform:translate({x:.1f}px,{y:.1f}px) scale({0.3 + 0.7 * k:.2f});"
                f"opacity:{0.1 + 0.9 * k ** 1.6:.2f}}}"
            )
        css.append(f"@keyframes g{ring}{{{''.join(frames)}}}")
        n = max(6, round(30 * math.cos(lat)))
        for i in range(n):
            delay = -period * i / n
            dots.append(f'<circle r="3.4" class="g" style="animation-name:g{ring};animation-delay:{delay:.2f}s"/>')
    # a small satellite on a tilted orbit, dimmed while it is behind the globe
    orb_a, orb_b = r * 1.32, r * 0.30
    frames = []
    for s in range(steps + 1):
        th = 2 * math.pi * s / steps
        x = cx + orb_a * math.sin(th)
        y = cy + orb_b * math.cos(th) - 0.18 * orb_a * math.sin(th)
        front = math.cos(th) > -0.05 or abs(orb_a * math.sin(th)) > r
        frames.append(f"{pct(s / steps)}{{transform:translate({x:.1f}px,{y:.1f}px);opacity:{1 if front else 0.15}}}")
    css.append(f"@keyframes sat{{{''.join(frames)}}}")
    css.append(f".g{{animation-duration:{period}s;animation-timing-function:linear;animation-iteration-count:infinite}}")
    css.append(f".sat{{animation:sat {period / 2.4:.2f}s linear infinite}}")
    rot = math.degrees(math.atan2(-0.18 * orb_a, orb_a))
    body = [
        f'<circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="{t["hair"]}"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="{orb_a:.1f}" ry="{orb_b:.1f}" fill="none" stroke="{t["hair"]}" '
        f'stroke-dasharray="2 5" transform="rotate({rot:.2f} {cx} {cy})"/>',
        f'<g fill="{t["ink"]}">{"".join(dots)}</g>',
        f'<rect class="sat" x="-4" y="-4" width="8" height="8" fill="{t["ink"]}"/>',
    ]
    return "\n".join(body), "".join(css)


def header(t):
    h = 380
    split = 820
    globe_svg, globe_css = globe(1010, 190, 96, t)
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
        globe_svg,
        mono(40, h - 26, TAGLINE, t["ink"]),
        mono(W - 58, h - 26, "NOW  /  NIMBUS", t["ink"], anchor="end"),
        f'<rect class="blink" x="{W - 50}" y="{h - 37}" width="8" height="13" fill="{t["ink"]}"/>',
        corner_marks(t, h),
    ]
    css = globe_css + "@keyframes blink{50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
    return svg(h, "\n".join(body), "Farhan Aulianda", css)


# ------------------------------------------------------- hooded hacker ----

# 40 x 36 sprite. H cloth, R rim/strings, V face shadow, E eyes, G screen
# reflection, L laptop lid, C cloud logo, K hands, D desk.
SPRITE = """
...............HHHHHHHHHH...............
.............HHHHHHHHHHHHHH.............
...........HHHHHHHHHHHHHHHHHH...........
..........HHHHHHHHHHHHHHHHHHHH..........
.........HHHHHHHRRRRRRRRHHHHHHH.........
........HHHHHHHRVVVVVVVVRHHHHHHH........
........HHHHHHRVVVVVVVVVVRHHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
........HHHHHRVVEEVVVVEEVVRHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
........HHHHHRVVVVVVVVVVVVRHHHHH........
.......HHHHHHRVVVVVVVVVVVVRHHHHHH.......
......HHHHHHHHRVVVVVVVVVVRHHHHHHHH......
.....HHHHHHHHHHRVVVVVVVVRHHHHHHHHHH.....
....HHHHHHHHHHHHRVVVVVVRHHHHHHHHHHHH....
...HHHHHHHHHHHHHHRRRRRRHHHHHHHHHHHHHH...
..HHHHHHHHHHHHHHHRHHHHRHHHHHHHHHHHHHHH..
..HHHHHHHHHHHHHHHRHHHHRHHHHHHHHHHHHHHH..
..HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLCCCLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLCCCCCLCCLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLCCCCCCCCCCLLLLLLHHHHHH..
..HHHHHHLLLLLLLLCCCCCCCCCCLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
..HHHHHHLLLLLLLLLLLLLLLLLLLLLLLLHHHHHH..
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
""".strip().splitlines()

COLOR_OF = {"H": "cloth", "R": "rim", "V": "void", "E": "eye", "L": "lid", "C": "logo", "D": "rim"}


def pixels(rows, x0, y0, px, t, only=None):
    """Run-length encode sprite rows into rects, one colour group at a time."""
    groups = {}
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            ch = row[i]
            if ch == "." or (only and ch not in only):
                i += 1
                continue
            k = i
            while k < len(row) and row[k] == ch:
                k += 1
            groups.setdefault(COLOR_OF[ch], []).append(
                f'<rect x="{x0 + i * px}" y="{y0 + j * px}" width="{(k - i) * px}" height="{px}"/>'
            )
            i = k
    return "".join(f'<g fill="{t[c]}">{"".join(r)}</g>' for c, r in groups.items())


def hacker(x0, y0, px, t):
    body = [f'<g shape-rendering="crispEdges">', pixels(SPRITE, x0, y0, px, t)]
    # screen light reflected inside the hood: short scan lines that scroll
    for n, (row, c0, c1) in enumerate(((12, 15, 20), (13, 17, 24), (14, 15, 22), (15, 18, 23))):
        body.append(
            f'<rect class="refl r{n}" x="{x0 + c0 * px}" y="{y0 + row * px}" '
            f'width="{(c1 - c0) * px}" height="{px - 2}" fill="{t["glow"]}"/>'
        )
    # eyelids close now and then
    body.append(
        f'<g class="lid" fill="{t["void"]}"><rect x="{x0 + 16 * px}" y="{y0 + 10 * px}" width="{2 * px}" height="{px}"/>'
        f'<rect x="{x0 + 22 * px}" y="{y0 + 10 * px}" width="{2 * px}" height="{px}"/></g>'
    )
    # two hands on the keyboard edge, tapping out of phase
    for side, col in (("hl", 3), ("hr", 34)):
        body.append(
            f'<rect class="{side}" x="{x0 + col * px}" y="{y0 + 33 * px}" width="{3 * px}" height="{2 * px}" fill="{t["hand"]}"/>'
        )
    body.append("</g>")
    css = (
        "@keyframes tapl{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
        "@keyframes tapr{0%,100%{transform:translateY(-6px)}50%{transform:translateY(0)}}"
        ".hl{animation:tapl .32s steps(1) infinite}.hr{animation:tapr .32s steps(1) infinite}"
        "@keyframes lid{0%,92%,100%{opacity:0}94%,97%{opacity:1}}.lid{animation:lid 5s steps(1) infinite}"
        "@keyframes refl{0%,100%{opacity:.15}50%{opacity:.75}}"
        ".refl{animation:refl 1.6s steps(4) infinite}"
        ".r1{animation-delay:-.4s}.r2{animation-delay:-.8s}.r3{animation-delay:-1.2s}"
    )
    return "".join(body), css


def terminal(t):
    h = 360
    px = 6
    sx, sy = 60, h - 40 - 36 * px  # sprite sits on the panel floor
    sprite, sprite_css = hacker(sx, sy, px, t)

    wx, wy, ww, wh = 360, 34, 800, h - 68
    cw, lh, fs = 12, 34, 20  # monospace cell: 0.6em wide
    tx, ty = wx + 30, wy + 82

    # timeline: commands type char by char, output lands at once
    cps = 0.055
    schedule, clock = [], 0.6
    for is_cmd, text in TERMINAL:
        dur = len(text) * cps if is_cmd else 0.05
        schedule.append((clock, clock + dur))
        clock += dur + (0.5 if is_cmd else 0.9)
    final = clock
    total = final + 4.5

    css = [sprite_css]
    lines = []
    for idx, ((is_cmd, text), (s, e)) in enumerate(zip(TERMINAL, schedule)):
        y = ty + idx * lh
        shown = ("$ " if is_cmd else "") + text
        n_chars = len(shown)
        fill = t["ink"] if is_cmd else t["mid"]
        width = n_chars * cw
        css.append(f"@keyframes v{idx}{{0%,{pct(s / total)}{{opacity:0}}{pct(s / total + 1e-4)},96%{{opacity:1}}97%,100%{{opacity:0}}}}")
        css.append(f".v{idx}{{animation:v{idx} {total:.2f}s steps(1) infinite}}")
        parts = [
            f'<text x="{tx}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{fill}" '
            f'textLength="{width}" lengthAdjust="spacing" xml:space="preserve">{escape(shown)}</text>'
        ]
        if is_cmd:
            n = len(text)
            css.append(
                f"@keyframes m{idx}{{0%{{transform:translateX(0)}}{pct(s / total)}{{transform:translateX(0);"
                f"animation-timing-function:steps({n},end)}}{pct(e / total)},100%{{transform:translateX({n * cw}px)}}}}"
                f".m{idx}{{animation:m{idx} {total:.2f}s infinite}}"
            )
            nxt = schedule[idx + 1][0] if idx + 1 < len(schedule) else final
            css.append(
                f"@keyframes c{idx}{{0%,{pct(nxt / total)},100%{{opacity:0}}"
                f"{pct(s / total)}{{opacity:1}}}}.c{idx}{{animation:m{idx} {total:.2f}s infinite,c{idx} {total:.2f}s steps(1) infinite}}"
            )
            x = tx + 2 * cw
            parts.append(f'<rect class="m{idx}" x="{x}" y="{y - 22}" width="{width}" height="{lh - 2}" fill="{t["panel"]}"/>')
            parts.append(f'<rect class="c{idx}" x="{x}" y="{y - 19}" width="{cw}" height="22" fill="{t["ink"]}"/>')
        lines.append(f'<g class="v{idx}">{"".join(parts)}</g>')

    # resting prompt with a blinking block once everything has been typed
    py = ty + len(TERMINAL) * lh
    css.append(f"@keyframes vp{{0%,{pct(final / total)}{{opacity:0}}{pct(final / total + 1e-4)},96%{{opacity:1}}97%,100%{{opacity:0}}}}")
    css.append(f".vp{{animation:vp {total:.2f}s steps(1) infinite}}")
    css.append("@keyframes blink{50%{opacity:0}}.blink{animation:blink 1s steps(1) infinite}")
    lines.append(
        f'<g class="vp"><text x="{tx}" y="{py}" font-family="{MONO}" font-size="{fs}" fill="{t["ink"]}">$</text>'
        f'<rect class="blink" x="{tx + 2 * cw}" y="{py - 19}" width="{cw}" height="22" fill="{t["ink"]}"/></g>'
    )

    scan = "".join(
        f'<rect x="{wx + 1}" y="{y}" width="{ww - 2}" height="1"/>' for y in range(wy + 46, wy + wh - 2, 4)
    )
    body = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{t["hair"]}"/>',
        corner_marks(t, h),
        mono(40, 30, "FIG. 01 — AT WORK", t["mid"], size=11),
        sprite,
        f'<rect x="{wx + .5}" y="{wy + .5}" width="{ww}" height="{wh}" fill="{t["panel"]}" stroke="{t["ink"]}"/>',
        f'<line x1="{wx}" y1="{wy + 40.5}" x2="{wx + ww}" y2="{wy + 40.5}" stroke="{t["ink"]}"/>',
        "".join(
            f'<rect x="{wx + 16 + i * 20}" y="{wy + 14}" width="11" height="11" fill="none" stroke="{t["ink"]}"/>'
            for i in range(3)
        ),
        mono(wx + ww / 2, wy + 25, f"farhan@{HANDLE}: ~/nimbus", t["mid"], size=12, anchor="middle", spacing=1),
        "".join(lines),
        f'<g fill="{t["ink"]}" opacity=".035">{scan}</g>',
    ]
    return svg(h, "\n".join(body), "A hooded hacker typing in a terminal", "".join(css))


# --------------------------------------------------------- nimbus card ----

CLOUD = """
....XXXX......
..XXXXXXXX.XX.
.XXXXXXXXXXXXX
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
.XXXXXXXXXXXX.
""".strip().splitlines()


def nimbus(t):
    h = 330
    body = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{t["hair"]}"/>',
        f'<line x1="640" y1="0" x2="640" y2="{h}" stroke="{t["hair"]}"/>',
        corner_marks(t, h),
        mono(40, 52, "FEATURED  /  OPEN SOURCE  /  MIT", t["mid"], size=12),
        f'<text x="36" y="148" font-family="{SANS}" font-weight="700" font-size="88" letter-spacing="-2" '
        f'fill="{t["ink"]}" textLength="400" lengthAdjust="spacingAndGlyphs">NIMBUS</text>',
        f'<text x="40" y="196" font-family="{SANS}" font-size="26" fill="{t["ink"]}">Learn cloud computing by playing.</text>',
        mono(40, 236, "BILINGUAL ID / EN  ·  NO SIGN-UP  ·  PHONE OR LAPTOP", t["mid"], size=12, spacing=1.6),
        mono(40, 286, "SVELTEKIT · SVELTE 5 · TYPESCRIPT · TAILWIND · BUN · CLOUDFLARE", t["ink"], size=12, spacing=1.6),
    ]

    # right side: a packet rides a cable through the cloud, like the cable lesson
    a, b = (720, 250), (1120, 250)
    path = f"M{a[0]} {a[1]} C {a[0] + 60} 70, {b[0] - 60} 70, {b[0]} {b[1]}"
    cloud_px, cx0, cy0 = 7, 920 - 7 * 7, 108
    body += [
        f'<path d="{path}" fill="none" stroke="{t["mid"]}" stroke-dasharray="3 6"/>',
        f'<g class="bob" shape-rendering="crispEdges" fill="{t["ink"]}">'
        + "".join(
            f'<rect x="{cx0 + i * cloud_px}" y="{cy0 + j * cloud_px}" width="{cloud_px}" height="{cloud_px}"/>'
            for j, row in enumerate(CLOUD) for i, ch in enumerate(row) if ch == "X"
        )
        + "</g>",
    ]
    for (x, y), label in ((a, "YOU"), (b, "SERVER")):
        body.append(f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" fill="{t["ink"]}"/>')
        body.append(mono(x, y + 36, label, t["mid"], size=11, anchor="middle", spacing=2))
    for delay in (0, 0.18, 0.36):
        size = 10 if delay == 0 else 6
        op = 1 if delay == 0 else 0.35
        body.append(
            f'<rect x="{-size / 2}" y="{-size / 2}" width="{size}" height="{size}" fill="{t["ink"]}" opacity="{op}">'
            f'<animateMotion dur="2.6s" begin="{-delay:.2f}s" repeatCount="indefinite" path="{path}" '
            f'keyPoints="0;1;1" keyTimes="0;0.7;1" calcMode="linear"/></rect>'
        )
    body += [
        mono(920, 298, "LATENCY", t["mid"], size=11, anchor="middle"),
        f'<g font-family="{MONO}" font-size="14" fill="{t["ink"]}" text-anchor="middle">'
        + "".join(f'<text class="ms ms{i}" x="920" y="276">{v} ms</text>' for i, v in enumerate((12, 38, 9, 74)))
        + "</g>",
    ]
    css = (
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
        ".bob{animation:bob 3s steps(6) infinite}"
        "@keyframes ms{0%,24.9%{opacity:1}25%,100%{opacity:0}}"
        ".ms{opacity:0;animation:ms 10.4s steps(1) infinite}"
        + "".join(f".ms{i}{{animation-delay:{-10.4 + i * 2.6:.1f}s}}" for i in range(4))
    )
    return svg(h, "\n".join(body), "Nimbus: learn cloud computing by playing", css)


# ----------------------------------------------------------- the rest ----

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
        f'<rect class="scan" x="170" y="0" width="2" height="56" fill="{t["mid"]}"/>',
        mono(W / 2, 82, "  ".join(HANDLE.upper()), t["mid"], size=12, anchor="middle", spacing=1),
    ]
    css = "@keyframes scan{0%{transform:translateX(0)}100%{transform:translateX(858px)}}.scan{animation:scan 3.2s ease-in-out infinite alternate}"
    return svg(h, "\n".join(body), "end of page", css)


# ------------------------------------------------------------- buttons ----

ICONS = {
    "cloud": """
...XXX...
.XXXXXX..
XXXXXXXXX
XXXXXXXXX
.XXXXXXX.
""",
    "play": """
XX.......
XXXX.....
XXXXXX...
XXXXXXXX.
XXXXXX...
XXXX.....
XX.......
""",
    "code": """
..X...X..
.X.....X.
X..X....X
X...X...X
X....X..X
.X.....X.
..X...X..
""",
    "instagram": """
.XXXXXXX.
X.....X.X
X..XXX..X
X.X...X.X
X.X...X.X
X.X...X.X
X..XXX..X
X.......X
.XXXXXXX.
""",
    "x": """
XX.....X.
.XX...X..
..XX.X...
...XX....
...XXX...
..X..XX..
.X....XX.
X......XX
""",
    "mail": """
XXXXXXXXX
XX.....XX
X.X...X.X
X..X.X..X
X...X...X
X.......X
XXXXXXXXX
""",
}

ARROW = """
..XXXXX
....XXX
...X.XX
..X...X
.X.....
X......
"""

BUTTONS = {
    # name: (icon, label, sub)
    "btn-nimbus": ("cloud", "NIMBUS", NIMBUS_URL),
    "btn-instagram": ("instagram", "INSTAGRAM", "@farhanaulianda.py"),
    "btn-x": ("x", "X / TWITTER", "@farhanaulianda"),
    "btn-email": ("mail", "EMAIL", "hi@farhanaulianda.my.id"),
    "btn-play": ("play", "PLAY NIMBUS", "open in browser"),
    "btn-source": ("code", "SOURCE", "github / nimbus"),
}


def bitmap(art, x0, y0, px, fill, cls=""):
    rows = art.strip().splitlines()
    rects = "".join(
        f'<rect x="{x0 + i * px}" y="{y0 + j * px}" width="{px}" height="{px}"/>'
        for j, row in enumerate(rows) for i, ch in enumerate(row) if ch == "X"
    )
    c = f' class="{cls}"' if cls else ""
    return f'<g{c} fill="{fill}" shape-rendering="crispEdges">{rects}</g>'


def button(t, icon, label, sub, delay):
    """A chunky retro key with a hard shadow; it presses itself now and then."""
    w, h, d = 420, 112, 8
    bw, bh = w - d - 4, h - d - 4
    face = [
        f'<rect x="2" y="2" width="{bw}" height="{bh}" fill="{t["panel"]}" stroke="{t["ink"]}" stroke-width="3"/>',
        f'<rect x="2" y="2" width="{bh}" height="{bh}" fill="{t["ink"]}"/>',
        bitmap(ICONS[icon], 2 + (bh - 9 * 6) / 2, 2 + (bh - len(ICONS[icon].strip().splitlines()) * 6) / 2, 6, t["panel"]),
        f'<text x="{bh + 24}" y="52" font-family="{MONO}" font-size="24" font-weight="700" letter-spacing="2" fill="{t["ink"]}">{label}</text>',
        f'<text x="{bh + 24}" y="80" font-family="{MONO}" font-size="15" fill="{t["mid"]}">{escape(sub)}</text>',
        bitmap(ARROW, bw - 44, 22, 4, t["ink"], "arrow"),
    ]
    body = [
        f'<rect x="{2 + d}" y="{2 + d}" width="{bw}" height="{bh}" fill="{t["ink"]}"/>',
        f'<g class="face">{"".join(face)}</g>',
    ]
    css = (
        "@keyframes press{0%,88%,96%,100%{transform:translate(0,0)}90%,94%{transform:translate(8px,8px)}}"
        f".face{{animation:press 7s steps(1) {delay:.1f}s infinite}}"
        "@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(4px,-4px)}}"
        ".arrow{animation:nudge 1.4s steps(2) infinite}"
    )
    out = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
    return out + f"<title>{label}</title><style>{css}</style>" + "".join(body) + "</svg>\n"


SECTIONS = ["WHOAMI", "NOW BUILDING", "TOOLBOX", "ACTIVITY"]


def section(t, idx, title):
    h = 96
    ticks = "".join(
        f'<line x1="{x + .5}" y1="{h - (8 if x % 100 == 0 else 3)}" x2="{x + .5}" y2="{h}"/>' for x in range(0, W + 1, 20)
    )
    tw = len(title) * 26 * 0.62 + 8
    body = [
        f'<text x="0" y="62" font-family="{SANS}" font-weight="700" font-size="56" fill="{t["ink"]}" '
        f'textLength="80" lengthAdjust="spacingAndGlyphs">{idx:02d}</text>',
        f'<rect x="100" y="24" width="2" height="44" fill="{t["ink"]}"/>',
        f'<text x="124" y="56" font-family="{MONO}" font-size="26" font-weight="700" letter-spacing="3" fill="{t["ink"]}">{title}</text>',
        f'<rect class="blink" x="{124 + tw + len(title) * 3}" y="36" width="14" height="24" fill="{t["ink"]}"/>',
        mono(W, 56, f"{idx:02d} / {len(SECTIONS):02d}", t["mid"], size=13, anchor="end"),
        f'<g stroke="{t["mid"]}">{ticks}</g>',
        f'<line x1="0" y1="{h - .5}" x2="{W}" y2="{h - .5}" stroke="{t["ink"]}"/>',
        f'<rect class="sweep" x="0" y="{h - 4}" width="60" height="4" fill="{t["ink"]}"/>',
    ]
    css = (
        "@keyframes blink{50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
        f"@keyframes sweep{{0%{{transform:translateX(0)}}100%{{transform:translateX({W - 60}px)}}}}"
        f".sweep{{animation:sweep 6s steps(57) {-idx * 1.3:.1f}s infinite alternate}}"
    )
    return svg(h, "\n".join(body), f"{idx:02d} {title}", css)


def main():
    OUT.mkdir(exist_ok=True)
    builds = {"header": header, "terminal": terminal, "nimbus": nimbus,
              "stack": stack, "footer": barcode}
    for theme, palette in THEMES.items():
        for name, build in builds.items():
            path = OUT / f"{name}-{theme}.svg"
            path.write_text(build(palette))
            print(f"assets/{path.name}  {path.stat().st_size // 1024} KB")
        for n, (name, (icon, label, sub)) in enumerate(BUTTONS.items()):
            (OUT / f"{name}-{theme}.svg").write_text(button(palette, icon, label, sub, delay=n * 1.2))
        for n, title in enumerate(SECTIONS, 1):
            (OUT / f"sec-{n}-{theme}.svg").write_text(section(palette, n, title))
    print(f"+ {len(BUTTONS)} buttons and {len(SECTIONS)} section titles per theme")


if __name__ == "__main__":
    main()
