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
TAGLINE = "FULL STACK  /  CLOUD ENGINEER"
SITE = "farhanaulianda.my.id"

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
    (False, "farhan aulianda  //  full stack & cloud engineer"),
    (True, "cat about.txt"),
    (False, "i build products from zero to one,"),
    (False, "shipping ai-powered tools for real users."),
    (True, f"open https://{SITE}"),
]

HIGHLIGHTS = [
    # icon, title, subtitle
    ("cloud", "AWS COMMUNITY BUILDER", "serverless"),
    ("star", "GOOGLE STUDENT AMBASSADOR", "campus developer community"),
]

THEMES = {
    "light": {
        "ink": "#0A0A0A", "mid": "#6E6E6E", "faint": "#A0A0A0", "hair": "#D0D7DE",
        "panel": "#F6F8FA",
        # hooded hacker palette
        "cloth": "#141414", "legs": "#3C3C3C", "rim": "#4A4A4A", "void": "#000000",
        "eye": "#FFFFFF", "lid": "#8C8C8C", "hand": "#9A9A9A", "glow": "#9A9A9A",
        "wood": "#C2C2C2", "mug": "#5A5A5A",
    },
    "dark": {
        "ink": "#F0F0F0", "mid": "#8B949E", "faint": "#6E7681", "hair": "#30363D",
        "panel": "#010409",
        "cloth": "#3A414A", "legs": "#262C33", "rim": "#6E7681", "void": "#000000",
        "eye": "#FFFFFF", "lid": "#D0D7DE", "hand": "#C9D1D9", "glow": "#C9D1D9",
        "wood": "#30363D", "mug": "#8B949E",
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
        mono(W - 58, h - 26, SITE.upper(), t["ink"], anchor="end"),
        f'<rect class="blink" x="{W - 50}" y="{h - 37}" width="8" height="13" fill="{t["ink"]}"/>',
        corner_marks(t, h),
    ]
    css = globe_css + "@keyframes blink{50%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}"
    return svg(h, "\n".join(body), "Farhan Aulianda", css)


# ------------------------------------------------------- hooded hacker ----

# The figure is described as simple shapes on a 64 x 48 grid and rasterized
# into pixels, so proportions stay right without hand-placing every square.
# Later layers paint over earlier ones.

def _in_poly(x, y, pts):
    inside = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _near_seg(x, y, a, b, w):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    k = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - x1 - k * dx, y - y1 - k * dy) <= w / 2


SCENE = [
    # stool and desk
    ("wood", "poly", [(9, 33), (25, 33), (25, 35), (9, 35)]),
    ("wood", "poly", [(16, 35), (18, 35), (18, 46), (16, 46)]),
    ("wood", "poly", [(11, 46), (23, 46), (23, 47), (11, 47)]),
    ("wood", "poly", [(34, 29), (64, 29), (64, 31), (34, 31)]),
    ("wood", "poly", [(59, 31), (61, 31), (61, 47), (59, 47)]),
    ("wood", "poly", [(36, 31), (38, 31), (38, 47), (36, 47)]),
    # legs
    ("legs", "seg", (15, 31.5), (31, 32.5), 4.2),
    ("legs", "seg", (30.5, 32.5), (31.5, 45), 3.4),
    ("legs", "poly", [(29, 45), (36, 45), (36, 47), (29, 47)]),
    # hunched torso
    ("cloth", "poly", [(19, 14), (16, 17), (14, 22), (13.5, 27), (14.5, 32), (16.5, 34.5),
                       (27, 34.5), (28.5, 29), (28.5, 22), (27, 17), (24, 14)]),
    # hood: rounded back, peak pushed forward over the face
    ("cloth", "circle", (21.5, 10.5), 6.8),
    ("cloth", "poly", [(20, 4), (27, 3.5), (32.5, 6.5), (31.5, 9), (27, 9)]),
    ("cloth", "poly", [(23, 14), (30, 13), (29, 17), (24, 18)]),
    # face in shadow, only the inner edge of the hood catches light
    ("rim", "poly", [(25, 8), (27, 8), (27, 15.5), (25, 15.5)]),
    ("void", "poly", [(26, 8.5), (30.5, 8.5), (31.8, 11.2), (30.6, 12), (31, 14), (29, 15.6), (26, 15.6)]),
    ("cloth", "poly", [(24, 3.5), (33.5, 6.2), (33, 8.6), (25, 9)]),
    # arm reaching for the keyboard
    ("cloth", "seg", (22, 18), (30, 24.5), 4.6),
    ("cloth", "seg", (30, 24.5), (39.5, 26.8), 3.6),
    # laptop: base on the desk, lid tilted back, screen facing the hacker
    ("lid", "poly", [(37, 27.6), (51, 27.6), (51, 29), (37, 29)]),
    ("lid", "seg", (50.5, 28), (53, 15.5), 1.6),
    # mug
    ("mug", "poly", [(55, 23.5), (59, 23.5), (59, 29), (55, 29)]),
    ("mug", "poly", [(59, 24.5), (61, 24.5), (61, 27.5), (59, 27.5)]),
    ("hole", "poly", [(59, 25.5), (60, 25.5), (60, 26.5), (59, 26.5)]),
]


def rasterize(w=64, h=48):
    grid = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            cx, cy = x + 0.5, y + 0.5
            for layer in SCENE:
                role, kind = layer[0], layer[1]
                hit = (
                    _in_poly(cx, cy, layer[2]) if kind == "poly"
                    else math.hypot(cx - layer[2][0], cy - layer[2][1]) <= layer[3] if kind == "circle"
                    else _near_seg(cx, cy, layer[2], layer[3], layer[4])
                )
                if hit:
                    grid[y][x] = role
    for y in range(h):
        for x in range(w):
            if grid[y][x] == "hole":
                grid[y][x] = None
    return grid


def pixels(grid, x0, y0, px, t):
    groups = {}
    for j, row in enumerate(grid):
        i = 0
        while i < len(row):
            role = row[i]
            k = i
            while k < len(row) and row[k] == role:
                k += 1
            if role:
                groups.setdefault(role, []).append(
                    f'<rect x="{x0 + i * px}" y="{y0 + j * px}" width="{(k - i) * px}" height="{px}"/>'
                )
            i = k
    return "".join(f'<g fill="{t[r]}">{"".join(v)}</g>' for r, v in groups.items())


def hacker(x0, y0, px, t):
    P = lambda gx, gy, gw=1, gh=1, **kw: (
        f'<rect x="{x0 + gx * px}" y="{y0 + gy * px}" width="{gw * px}" height="{gh * px}"'
        + "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items()) + "/>"
    )
    body = ['<g shape-rendering="crispEdges">', pixels(rasterize(), x0, y0, px, t)]
    # light from the screen washes over the face
    cone = " ".join(f"{x0 + gx * px:.1f},{y0 + gy * px:.1f}" for gx, gy in ((51.5, 16), (51, 28), (30, 15.5), (31, 8)))
    body.append(f'<polygon class="cone" points="{cone}" fill="{t["glow"]}"/>')
    body.append(f'<g class="lit" fill="{t["glow"]}">{P(31, 10)}{P(31, 11)}{P(30, 12)}{P(30, 13)}{P(29, 14)}</g>')
    body.append(f'<g class="eye" fill="{t["eye"]}">{P(29, 10)}</g>')
    # hand tapping the keys
    body.append(f'<g class="hand" fill="{t["hand"]}">{P(39, 26, 3, 1)}{P(41, 27)}</g>')
    # steam off the mug
    for n, gx in enumerate((56, 57.5)):
        body.append(f'<g class="steam s{n}" fill="{t["glow"]}">{P(gx, 21)}{P(gx + 1, 19)}{P(gx, 17)}</g>')
    body.append("</g>")
    css = (
        "@keyframes tap{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
        ".hand{animation:tap .28s steps(1) infinite}"
        "@keyframes cone{0%,100%{opacity:.07}30%{opacity:.16}60%{opacity:.04}80%{opacity:.12}}"
        ".cone{animation:cone 2.2s steps(4) infinite}"
        "@keyframes lit{0%,100%{opacity:.55}40%{opacity:1}70%{opacity:.35}}.lit{animation:lit 1.2s steps(3) infinite}"
        "@keyframes eye{0%,90%,100%{opacity:1}93%,96%{opacity:0}}.eye{animation:eye 4.5s steps(1) infinite}"
        "@keyframes steam{0%{transform:translateY(8px);opacity:0}30%{opacity:.9}100%{transform:translateY(-12px);opacity:0}}"
        ".steam{animation:steam 2.6s steps(6) infinite}.s1{animation-delay:-1.3s}"
    )
    return "".join(body), css


def terminal(t):
    h = 360
    px = 5
    sx, sy = 24, h - 26 - 48 * px  # sprite sits on the panel floor
    sprite, sprite_css = hacker(sx, sy, px, t)

    wx, wy, ww, wh = 360, 34, 800, h - 68
    cw, lh, fs = 12, 32, 20  # monospace cell: 0.6em wide
    tx, ty = wx + 30, wy + 76

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
        mono(wx + ww / 2, wy + 25, f"farhan@{HANDLE}: ~", t["mid"], size=12, anchor="middle", spacing=1),
        f'<clipPath id="screen"><rect x="{wx + 1}" y="{wy + 41}" width="{ww - 1}" height="{wh - 41}"/></clipPath>',
        f'<g clip-path="url(#screen)">{"".join(lines)}</g>',
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
        mono(40, 52, "STAR PROJECT  /  OPEN SOURCE  /  MIT", t["mid"], size=12),
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
    "globe": """
..XXXXX..
.X..X..X.
X..X.X..X
XXXXXXXXX
X..X.X..X
.X..X..X.
..XXXXX..
""",
    "star": """
....X....
....X....
...XXX...
XXXXXXXXX
.XXXXXXX.
..XXXXX..
..XX.XX..
.XX...XX.
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
    "btn-portfolio": ("globe", "PORTFOLIO", SITE),
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


def highlights(t):
    h = 132
    cw = W / len(HIGHLIGHTS)
    body = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{t["hair"]}"/>']
    for n, (icon, title, sub) in enumerate(HIGHLIGHTS):
        x = n * cw
        if n:
            body.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{t["hair"]}"/>')
        rows = len(ICONS[icon].strip().splitlines())
        body += [
            f'<rect x="{x + 28}" y="30" width="72" height="72" fill="{t["ink"]}"/>',
            bitmap(ICONS[icon], x + 28 + (72 - 9 * 6) / 2, 30 + (72 - rows * 6) / 2, 6, t["panel"]),
            mono(x + 122, 58, title, t["ink"], size=17, spacing=1.6, extra=' font-weight="700"'),
            mono(x + 122, 86, sub, t["mid"], size=14, spacing=.6),
            f'<rect class="hl h{n}" x="{x}" y="{h - 4}" width="{cw}" height="4" fill="{t["ink"]}"/>',
        ]
    k = len(HIGHLIGHTS)
    css = (
        f"@keyframes hl{{0%,{100 / k:.2f}%{{opacity:1}}{100 / k + .01:.2f}%,100%{{opacity:0}}}}"
        f".hl{{opacity:0;animation:hl {k * 2.4}s steps(1) infinite}}"
        + "".join(f".h{n}{{animation-delay:{-(k - n) * 2.4:.1f}s}}" for n in range(k))
    )
    return svg(h, "\n".join(body), "Highlights", css)


SECTIONS = ["WHOAMI", "STAR PROJECT", "TOOLBOX", "ACTIVITY"]


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
    builds = {"header": header, "terminal": terminal, "highlights": highlights, "nimbus": nimbus,
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
