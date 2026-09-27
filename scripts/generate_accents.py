"""Generate original animated SVG accents and contact badges, without dependencies."""

from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import INK, MUTED

ROOT = Path(__file__).resolve().parent.parent
PURPLE = "#9391FF"


def typing():
    roles = ["Full-stack developer", "Blockchain developer", "Computer vision builder"]
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="560" height="64" viewBox="0 0 560 64" role="img" aria-labelledby="title">
<title id="title">Full-stack developer · Blockchain developer · Computer vision builder</title>
<style>
text { font-family: 'Courier New',monospace; font-size: 25px; fill: #9391FF; }
.extra { display:none; }
.cursor { opacity:0; }
@media (prefers-reduced-motion: no-preference) {
 .extra { display:inline; }
 .reveal { animation: type 15s steps(var(--chars),end) infinite both; animation-delay:var(--delay); }
 .cursor { opacity:1; animation: follow 15s steps(var(--chars),end) infinite both; animation-delay:var(--delay); }
 .blink { animation: blink 1s step-end infinite; }
}
@keyframes type { 0%,2% {width:0} 17%,26% {width:var(--width)} 32%,100% {width:0} }
@keyframes follow { 0% {transform:translateX(0);opacity:0} 2% {transform:translateX(0);opacity:1} 17%,26% {transform:translateX(var(--width));opacity:1} 32% {transform:translateX(0);opacity:1} 33%,100% {transform:translateX(0);opacity:0} }
@keyframes blink { 50% {opacity:0} }
</style>
<text x="4" y="42" aria-hidden="true">&gt;</text>''']
    for i, role in enumerate(roles):
        width = len(role) * 15
        style = f"--width:{width}px;--chars:{len(role)};--delay:{i * 5}s"
        parts.append(f'''<g class="{'extra' if i else 'first'}" style="{style}">
<defs><clipPath id="role{i}"><rect class="reveal" x="32" y="12" width="{width}" height="40"/></clipPath></defs>
<text x="32" y="42" textLength="{width}" lengthAdjust="spacingAndGlyphs" clip-path="url(#role{i})">{escape(role)}</text>
<g class="cursor"><rect class="blink" x="{34}" y="21" width="2" height="26" fill="{PURPLE}"/></g>
</g>''')
    return "\n".join(parts) + "</svg>\n"


TICKER = [("OPEN TO WORK", "#B1AEFF"), ("GEBZE, TÜRKİYE", MUTED),
          ("BLOCKSCOUT PRIZE @ ETHGLOBAL PRAGUE", INK), ("ENS PRIZE @ ETHROME", INK),
          ("GTU BLOCKCHAIN · SOFTWARE VP", INK), ("SOLIDITY", MUTED), ("TYPESCRIPT", MUTED),
          ("PYTHON", MUTED), ("REACT NATIVE", MUTED), ("YOLOv8", MUTED), ("SPRING BOOT", MUTED)]
TICKER_CHAR = 7.8  # 13px monospace advance, enforced with textLength


def ticker(width):
    parts, x = [], 0.0
    for label, colour in TICKER:
        length = len(label) * TICKER_CHAR
        parts.append(f'<text x="{x:.1f}" y="25" fill="{colour}" textLength="{length:.1f}" '
                     f'lengthAdjust="spacingAndGlyphs">{escape(label)}</text>')
        x += length + 18
        parts.append(f'<rect x="{x + 2:.1f}" y="15" width="2" height="6" fill="{PURPLE}"/>'
                     f'<rect x="{x:.1f}" y="17" width="6" height="2" fill="{PURPLE}"/>')
        x += 24
    strip = "".join(parts)
    seconds = x / 45
    label = " · ".join(item for item, _ in TICKER)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="40" viewBox="0 0 {width} 40" role="img" aria-label="{escape(label)}">
<style>
text {{font-family:'Courier New',ui-monospace,monospace;font-size:13px;font-weight:700}}
.strip {{transform:translateX(16px)}}
@media (prefers-reduced-motion: no-preference) {{
 .strip {{animation:scroll {seconds:.1f}s linear infinite}}
}}
@keyframes scroll {{from {{transform:translateX(0)}} to {{transform:translateX(-{x:.1f}px)}}}}
</style>
<defs>
<clipPath id="inside"><rect x="1" y="1" width="{width - 2}" height="38" rx="7"/></clipPath>
<linearGradient id="fade-left"><stop offset="0" stop-color="#17151F"/><stop offset="1" stop-color="#17151F" stop-opacity="0"/></linearGradient>
<linearGradient id="fade-right"><stop offset="0" stop-color="#17151F" stop-opacity="0"/><stop offset="1" stop-color="#17151F"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{width - 1}" height="39" rx="8" fill="#17151F" stroke="#3B354E"/>
<g clip-path="url(#inside)" shape-rendering="crispEdges">
<g class="strip"><g>{strip}</g><g transform="translate({x:.1f} 0)">{strip}</g></g>
<rect x="1" y="1" width="40" height="38" fill="url(#fade-left)"/>
<rect x="{width - 41}" y="1" width="40" height="38" fill="url(#fade-right)"/>
</g>
</svg>
'''


def badge(label, symbol, width):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="32" viewBox="0 0 {width} 32" role="img" aria-label="{label}">
<rect x=".5" y=".5" width="{width-1}" height="31" rx="7" fill="#17151F" stroke="#3B354E"/>
<text x="12" y="21" fill="{PURPLE}" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700">{symbol}</text>
<text x="38" y="21" fill="#EDEDEF" font-family="Arial,Helvetica,sans-serif" font-size="12">{label}</text>
</svg>\n'''


if __name__ == "__main__":
    assets = ROOT / "assets"
    files = {"typing.svg": typing(), "ticker.svg": ticker(880), "ticker-mobile.svg": ticker(440),
             "website.svg": badge("Website", "&lt;/&gt;", 108),
             "linkedin.svg": badge("LinkedIn", "in", 109),
             "email.svg": badge("Email", "@", 92)}
    for name, content in files.items():
        (assets / name).write_text(content, encoding="utf-8")
        print(f"Generated assets/{name}")
