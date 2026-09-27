"""Generate self-contained profile banners. Run: python3 scripts/generate_profile.py.

Standard library only; deterministic, no network requests or external fonts.
The unanimated SVG is complete; CSS adds motion only when the viewer permits it.
"""

from html import escape
from math import cos, sin, pi
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BG, INK, MUTED, ACCENT = "#0D0D0F", "#EDEDEF", "#A1A1AA", "#9391FF"


def contours(cx, cy, scale):
    paths = []
    for ring in range(19):
        radius = 39 + ring * 16
        points = []
        for step in range(145):
            angle = step * 2 * pi / 144
            ripple = 1 + .12 * sin(3 * angle + .4) + .07 * cos(5 * angle - ring * .035)
            x = cx + cos(angle) * radius * ripple * scale
            y = cy + sin(angle) * radius * ripple * .72 * scale
            points.append(f"{x:.2f},{y:.2f}")
        accent = ring % 5 == 1
        paths.append(f'<path class="{"contour" if accent else "terrain"}" '
                     f'd="M {" L ".join(points)} Z" fill="none" '
                     f'stroke="{ACCENT if accent else "#63636F"}" '
                     f'stroke-opacity="{.36 if accent else .19}" stroke-width="1"/>')
    return "\n".join(paths)


def monogram(x, y, cell=7, row_height=10):
    rows = []
    for row in range(25):
        line = []
        for col in range(35):
            leg = col < 5 or col >= 30
            diagonal = row < 18 and (abs(col - (3 + row * .8)) < 2.8
                                      or abs(col - (31 - row * .8)) < 2.8)
            line.append(("M#+:"[(row + col // 3) % 4]) if leg or diagonal else " ")
        rows.append(f'<text class="ascii" x="{x}" y="{y + row * row_height}" '
                    f'style="--delay:{row * 28}ms" xml:space="preserve" '
                    f'textLength="{35 * cell}" lengthAdjust="spacingAndGlyphs">'
                    f'{escape("".join(line))}</text>')
    return "\n".join(rows)


def banner(mobile=False):
    w, h = (600, 570) if mobile else (1200, 460)
    name_x, name_y, font_size = (36, 113, 62) if mobile else (56, 195, 80)
    mono_x, mono_y = (345, 337) if mobile else (866, 125)
    mono_cell, mono_row = (5.7, 8) if mobile else (7, 10)
    subtitle = ('<tspan x="36" dy="0">Full-stack · Blockchain</tspan>'
                '<tspan x="36" dy="32">Vision &amp; inference</tspan>') if mobile else 'Full-stack · Blockchain · Vision &amp; inference'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">Melik Ahmet Caymazoğlu</title>
<desc id="desc">Full-stack, blockchain, vision and inference. Purple topographic contours surround an ASCII M monogram.</desc>
<defs>
  <linearGradient id="shade"><stop offset="0" stop-color="{BG}"/><stop offset=".62" stop-color="{BG}" stop-opacity=".93"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  text {{ font-family: Arial, Helvetica, sans-serif; }}
  .ascii {{ font-family: 'Courier New', monospace; font-size: {mono_row}px; fill: {ACCENT}; }}
  @media (prefers-reduced-motion: no-preference) {{
    .ascii {{ animation: reveal 650ms ease-out both; animation-delay: var(--delay); }}
    .contour {{ animation: breathe 7s ease-in-out infinite; }}
  }}
  @keyframes reveal {{ from {{ opacity: .12; }} to {{ opacity: 1; }} }}
  @keyframes breathe {{ 0%, 100% {{ stroke-opacity: .25; }} 50% {{ stroke-opacity: .55; }} }}
</style>
<rect width="{w}" height="{h}" rx="16" fill="{BG}"/>
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">
{contours(470 if mobile else 990, 425 if mobile else 220, 1.15)}
<rect width="{w}" height="{h}" fill="url(#shade)"/>
{monogram(mono_x, mono_y, mono_cell, mono_row)}
</svg>
<text x="{name_x}" y="{49 if mobile else 58}" fill="{INK}" font-size="{23 if mobile else 25}" font-weight="700" letter-spacing="-1">melik<tspan fill="{ACCENT}">.</tspan></text>
<text x="{name_x}" y="{name_y}" fill="{INK}" font-size="{font_size}" font-weight="700" letter-spacing="-3">
  <tspan x="{name_x}">Melik Ahmet</tspan><tspan x="{name_x}" dy="{70 if mobile else 87}">Caymazoğlu</tspan>
</text>
<text x="{name_x}" y="{239 if mobile else 341}" fill="{MUTED}" font-size="{25 if mobile else 25}">{subtitle}</text>
<line x1="{name_x}" y1="{528 if mobile else 408}" x2="{w - name_x}" y2="{528 if mobile else 408}" stroke="#2B2B35"/>
<text x="{name_x}" y="{553 if mobile else 436}" fill="{MUTED}" font-size="{17 if mobile else 16}">Gebze, Türkiye</text>
<text x="{w - name_x}" y="{553 if mobile else 436}" text-anchor="end" fill="{ACCENT}" font-size="{17 if mobile else 16}">melik.dev</text>
</svg>
'''


if __name__ == "__main__":
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for mobile in (False, True):
        path = assets / ("profile-hero-mobile.svg" if mobile else "profile-hero.svg")
        path.write_text(banner(mobile), encoding="utf-8")
        print(f"Generated {path.relative_to(ROOT)}")
