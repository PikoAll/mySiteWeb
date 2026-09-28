#!/usr/bin/env python3
"""Generate images/brand/header-circuit.svg, the circuit background of the header.

A vector image instead of the old banner.webp (1024px stretched to ~2000px):
sharp at any width and DPR. Traces run from the left and right edges towards
the middle, bend at 45 degrees and end on a pad; the middle stays empty for
the PIKOBIT wordmark. Same palette as the site (--color-accent, white).
Deterministic (fixed seed): running it twice writes the same file.

Usage: python3 scripts/gen_header_circuit.py
"""
import random
from pathlib import Path

W, H = 1600, 200
CX = W / 2
CLEAR = 260  # half-width of the empty band behind the wordmark
OUT = Path(__file__).resolve().parent.parent / "images" / "brand" / "header-circuit.svg"


def half(rng):
    """Traces of the left half as (points, color, opacity, width)."""
    traces = []
    rows = list(range(10, H - 4, 9))
    for y in rows:
        if rng.random() < 0.12:
            continue
        x_end = CX - CLEAR - rng.uniform(0, 260)
        bend = rng.uniform(0.35, 0.8) * x_end
        dy = rng.choice([-1, 1]) * rng.uniform(8, 34)
        y2 = min(H - 8, max(8, y + dy))
        x2 = bend + abs(y2 - y)
        pts = [(0, y), (bend, y), (x2, y2), (max(x2 + 10, x_end), y2)]
        bright = rng.random() < 0.3
        color = "#00bfff" if bright else "#ffffff"
        opacity = 0.55 if bright else 0.14
        traces.append((pts, color, opacity, rng.choice([2, 2, 3])))
    # short vertical traces from the top and bottom edges, beside the band
    for x in range(40, int(CX - CLEAR), 46):
        if rng.random() < 0.45:
            continue
        top = rng.random() < 0.5
        y0 = 0 if top else H
        run = rng.uniform(18, 60)
        y1 = y0 + run if top else y0 - run
        side = rng.uniform(10, 30)
        y2 = y1 + side if top else y1 - side
        pts = [(x, y0), (x, y1), (x + side, y2)]
        bright = rng.random() < 0.25
        traces.append((pts, "#00bfff" if bright else "#ffffff", 0.5 if bright else 0.12, 2))
    return traces


def mirror(traces):
    return [([(W - x, y) for x, y in pts], c, o, w) for pts, c, o, w in traces]


def render(traces):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid slice">'
    ]
    for pts, color, opacity, width in traces:
        d = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        ex, ey = pts[-1]
        out.append(
            f'<g stroke="{color}" stroke-opacity="{opacity}" fill="none" '
            f'stroke-width="{width}"><path d="{d}"/>'
            f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="{width + 3}"/></g>'
        )
    out.append("</svg>\n")
    return "".join(out)


def main():
    left = half(random.Random(2026))
    OUT.write_text(render(left + mirror(left)), encoding="utf-8")
    print(f"{OUT} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
