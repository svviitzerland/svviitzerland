#!/usr/bin/env python3
"""Render the contribution calendar as a monochrome, animated SVG.

Runs in GitHub Actions (see .github/workflows/contributions.yml) with the
workflow's GITHUB_TOKEN. For a local preview without network access:

    python3 scripts/build-contrib.py --demo --out preview
"""
import argparse
import datetime as dt
import json
import os
import random
import urllib.request
from pathlib import Path

W = 1200
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
THEMES = {
    "light": {"ink": "#0A0A0A", "mid": "#6E6E6E", "faint": "#C8CDD3", "hair": "#D0D7DE"},
    "dark": {"ink": "#F0F0F0", "mid": "#8B949E", "faint": "#30363D", "hair": "#30363D"},
}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [(d["date"], d["contributionCount"], LEVELS[d["contributionLevel"]]) for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]
    return cal["totalContributions"], weeks


def demo():
    rng = random.Random(7)
    start = dt.date.today() - dt.timedelta(days=dt.date.today().weekday() + 1 + 52 * 7)
    weeks, total = [], 0
    for w in range(53):
        week = []
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            if day > dt.date.today():
                break
            n = max(0, int(rng.gauss(3, 5)))
            total += n
            week.append((day.isoformat(), n, min(4, (n + 2) // 3) if n else 0))
        weeks.append(week)
    return total, weeks


def streaks(days):
    longest = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    for i, (_, n, _) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i:  # an empty today does not break the streak yet
            break
    return current, longest


def render(t, total, weeks):
    days = [d for w in weeks for d in w]
    current, longest = streaks(days)
    best = max(days, key=lambda d: d[1])
    pitch, x0, y0 = 20, 92, 112
    sweep = 4.2  # seconds for the scan beam to cross the grid
    cycle = 10.0
    ncols = len(weeks)
    gx1 = x0 + ncols * pitch
    h = 396

    dots, months, last_month = [], [], None
    for c, week in enumerate(weeks):
        for date, n, level in week:
            r = (1.8, 3.4, 4.8, 6.2, 7.8)[level]
            row = dt.date.fromisoformat(date).isoweekday() % 7
            cx, cy = x0 + c * pitch + pitch / 2, y0 + row * pitch + pitch / 2
            fill = t["faint"] if level == 0 else t["ink"]
            dots.append(
                f'<circle class="d" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
                f'style="animation-delay:{c / ncols * sweep:.2f}s"><title>{date}: {n}</title></circle>'
            )
        first = dt.date.fromisoformat(week[0][0])
        # label a month on the week it starts in, so labels never collide
        if first.month != last_month and first.day <= 7 and c < ncols - 2:
            months.append(f'<text x="{x0 + c * pitch + 4}" y="{y0 - 14}">{first.strftime("%b").upper()}</text>')
            last_month = first.month

    def stat(x, label, value, unit):
        return (
            f'<text x="{x}" y="{h - 70}" font-family="{MONO}" font-size="11" letter-spacing="2.4" fill="{t["mid"]}">{label}</text>'
            f'<text x="{x}" y="{h - 26}" font-family="{SANS}" font-weight="700" font-size="40" fill="{t["ink"]}">{value}'
            f'<tspan font-family="{MONO}" font-weight="400" font-size="13" fill="{t["mid"]}" dx="8">{unit}</tspan></text>'
        )

    best_date = dt.date.fromisoformat(best[0]).strftime("%d %b").upper()
    sx = [40, 340, 640, 940]
    body = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{t["hair"]}"/>',
        f'<text x="40" y="44" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{t["ink"]}">'
        f'&gt; scan --user svviitzerland --range 365d</text>',
        f'<text class="st st0" x="{W - 40}" y="44" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{t["mid"]}" text-anchor="end">SCANNING…</text>',
        f'<text class="st st1" x="{W - 40}" y="44" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{t["ink"]}" text-anchor="end">[ OK ] {total:,} CONTRIBUTIONS</text>',
        f'<line x1="0" y1="64" x2="{W}" y2="64" stroke="{t["hair"]}"/>',
        f'<g font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{t["mid"]}">{"".join(months)}'
        + "".join(f'<text x="40" y="{y0 + r * pitch + 14}">{d}</text>' for r, d in ((1, "MON"), (3, "WED"), (5, "FRI")))
        + "</g>",
        f'<g>{"".join(dots)}</g>',
        f'<g class="beam"><rect x="-26" y="{y0 - 6}" width="26" height="{7 * pitch + 12}" fill="{t["ink"]}" opacity=".07"/>'
        f'<rect x="-1" y="{y0 - 10}" width="2" height="{7 * pitch + 20}" fill="{t["ink"]}"/></g>',
        f'<line x1="0" y1="{h - 112}" x2="{W}" y2="{h - 112}" stroke="{t["hair"]}"/>',
        "".join(f'<line x1="{x - 18}" y1="{h - 112}" x2="{x - 18}" y2="{h}" stroke="{t["hair"]}"/>' for x in sx[1:]),
        stat(sx[0], "LAST 365 DAYS", f"{total:,}", "contributions"),
        stat(sx[1], "CURRENT STREAK", current, "days"),
        stat(sx[2], "LONGEST STREAK", longest, "days"),
        stat(sx[3], "BEST DAY", best[1], best_date),
    ]
    end = sweep / cycle
    css = (
        ".d{transform-box:fill-box;transform-origin:center;"
        f"animation:pop {cycle}s linear infinite both}}"
        "@keyframes pop{0%{transform:scale(.25);opacity:.25}3%{transform:scale(1.35);opacity:1}"
        "6%,82%{transform:scale(1);opacity:1}92%,100%{transform:scale(.25);opacity:.25}}"
        f"@keyframes beam{{0%{{transform:translateX({x0}px);opacity:1}}{end * 100:.1f}%{{transform:translateX({gx1}px);opacity:1}}"
        f"{end * 100 + .1:.1f}%,100%{{transform:translateX({gx1}px);opacity:0}}}}"
        f".beam{{animation:beam {cycle}s linear infinite}}"
        f"@keyframes st0{{0%,{end * 100:.1f}%{{opacity:1}}{end * 100 + .1:.1f}%,100%{{opacity:0}}}}"
        f"@keyframes st1{{0%,{end * 100:.1f}%{{opacity:0}}{end * 100 + .1:.1f}%,100%{{opacity:1}}}}"
        f".st0{{animation:st0 {cycle}s steps(1) infinite}}.st1{{animation:st1 {cycle}s steps(1) infinite}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
        f'aria-label="{total} contributions in the last year">\n<title>{total} contributions in the last year</title>\n'
        f"<style>{css}</style>\n" + "\n".join(body) + "\n</svg>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="svviitzerland")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--demo", action="store_true", help="random data, no network")
    args = ap.parse_args()
    total, weeks = demo() if args.demo else fetch(args.user, os.environ["GITHUB_TOKEN"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme, palette in THEMES.items():
        (out / f"contributions-{theme}.svg").write_text(render(palette, total, weeks))
        print(out / f"contributions-{theme}.svg")


if __name__ == "__main__":
    main()
