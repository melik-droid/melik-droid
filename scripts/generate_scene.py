"""Generate the pixel desk scene and the pixel icons.

Run: python3 scripts/generate_scene.py. Standard library only, deterministic.
Every SVG is complete without animation; motion is added only when the viewer
has not asked for reduced motion.
"""

from html import escape
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import ACCENT, BG, ICONS, INK, MUG, PLANT, icon, sprite

ROOT = Path(__file__).resolve().parent.parent

# Edit these to change what the little terminal says.
NOW = [("building", "MacCleaner"), ("learning", "Bayesian inference"), ("status", "open to work")]

CHAR = 10.2  # monospace advance at 17px; text is forced to this width with textLength

# Code that scrolls up beside the monitor, loosely based on things I've built.
CODE = [
    "contract ChronoTrade {",
    "  mapping(address=>uint) t;",
    "  function trade(uint id)",
    "    external {",
    "    require(t[msg.sender]);",
    "    emit Traded(id);",
    "  }",
    "}",
    "",
    "const res = await fetch(u);",
    "const win = brawl(a, b);",
    "if (win) mintBadge(ens);",
    "",
    'model = YOLO("ppe.pt")',
    "for f in camera.stream():",
    "    hits = model(f)[0]",
    "    alert(hits.no_helmet)",
    "",
    "$ git push origin main",
    "$ docker compose up -d",
    "",
]
CODE_CHAR, CODE_LINE = 7.8, 19  # 13px monospace advance and line height
KEYWORDS = {"contract", "mapping", "function", "external", "require", "emit", "const", "await",
            "if", "for", "in", "address", "uint"}


def terminal_lines():
    prompt = (f'<tspan fill="{ACCENT}">melik@dev</tspan><tspan fill="#77748F">:~$ </tspan>', 13)
    lines = [(prompt[0] + f'<tspan fill="{INK}">now</tspan>', 16)]
    for label, value in NOW:
        if len(value) > 18:
            raise ValueError(f"'{value}' is too long for the terminal (18 characters max)")
        colour = "#B1AEFF" if label == "status" else INK
        lines.append((f'<tspan fill="#77748F">{label:<10}</tspan><tspan fill="{colour}">{escape(value)}</tspan>',
                      10 + len(value)))
    lines.append(prompt)
    return lines


def highlight(line):
    if line.startswith("$ "):
        return f'<tspan fill="#77748F">$ </tspan><tspan fill="{INK}">{escape(line[2:])}</tspan>'
    out = []
    tokens = re.findall(r'"[^"]*"|\w+|\s+|[^\w\s"]+', line)
    for index, token in enumerate(tokens):
        following = tokens[index + 1] if index + 1 < len(tokens) else ""
        if token.startswith('"'):
            colour = "#9DBAA5"
        elif token in KEYWORDS:
            colour = ACCENT
        elif token.isdigit():
            colour = "#C5BCFF"
        elif re.fullmatch(r"\w+", token) and following.startswith("("):
            colour = "#B1AEFF"
        elif re.fullmatch(r"\w+", token):
            colour = "#D4D3DE"
        else:
            colour = "#77748F"
        out.append(f'<tspan fill="{colour}">{escape(token)}</tspan>')
    return "".join(out)


def code_stream(x, y, width, height):
    block = []
    for index, line in enumerate(CODE):
        if len(line) * CODE_CHAR > width:
            raise ValueError(f"code line too wide for the stream: {line!r}")
        if line:
            block.append(f'<text class="code" x="{x}" y="{y + 14 + index * CODE_LINE}" '
                         f'textLength="{len(line) * CODE_CHAR:.1f}" lengthAdjust="spacingAndGlyphs" '
                         f'xml:space="preserve">{highlight(line)}</text>')
    loop = len(CODE) * CODE_LINE
    lines = "".join(block)
    return loop, (f'<g clip-path="url(#stream)"><g class="scroll">'
                  f'<g>{lines}</g><g transform="translate(0 {loop})">{lines}</g></g></g>'
                  f'<rect x="{x}" y="{y}" width="{width}" height="36" fill="url(#fade-top)"/>'
                  f'<rect x="{x}" y="{y + height - 36}" width="{width}" height="36" fill="url(#fade-bottom)"/>')


def desk():
    w, h = 640, 320
    lines = terminal_lines()
    windows = [(3, 12), (18, 30), (34, 50), (54, 64)]  # typing window per line, % of the loop
    text, covers, keyframes = [], [], []
    for i, (markup, chars) in enumerate(lines):
        y = 86 + i * 28
        length = chars * CHAR
        text.append(f'<text x="64" y="{y}" textLength="{length:.1f}" lengthAdjust="spacingAndGlyphs" '
                    f'xml:space="preserve">{markup}</text>')
        if i < len(windows):
            start, end = windows[i]
            cover = length + 8
            covers.append(f'<rect class="cover" style="animation:line{i} 16s steps({chars},end) infinite" x="60" y="{y - 19}" '
                          f'width="{cover:.1f}" height="26" fill="{BG}"/>')
            keyframes.append(f'@keyframes line{i} {{0%,{start}% {{transform:translateX(0)}} '
                             f'{end}%,93% {{transform:translateX({cover:.1f}px)}} 94%,100% {{transform:translateX(0)}}}}')
    prompt = text.pop()  # the closing prompt appears with its caret once typing is done
    caret_x = 64 + 13 * CHAR + 2
    caret_y = 86 + (len(lines) - 1) * 28 - 15

    sx, sy, sw, sh = 416, 24, 212, 180
    loop, stream = code_stream(sx, sy, sw, sh)

    keys = "".join(f'<rect x="{100 + col * 13}" y="{253 + row * 4}" width="10" height="2" fill="#77748F"/>'
                   for row in range(2) for col in range(20))

    steam = "".join(
        f'<g class="steam" style="animation-delay:-{i}s" fill="#77748F">'
        f'<rect x="{430 + i * 7}" y="214" width="4" height="4"/><rect x="{434 + i * 7}" y="206" width="4" height="4"/></g>'
        for i in range(3))

    status = ", ".join(f"{label}: {value}" for label, value in NOW)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">Now — {escape(status)}</title>
<desc id="desc">A purple pixel desk. The monitor types out what I am building and learning while code scrolls past beside it.</desc>
<style>
text {{font-family:'Courier New',ui-monospace,monospace;font-size:17px}}
.code {{font-size:13px}}
.cover {{display:none}}
@media (prefers-reduced-motion: no-preference) {{
 .cover {{display:inline}}
 .caret-group {{animation:caret 16s linear infinite}}
 .caret {{animation:blink 1s step-end infinite}}
 .scroll {{animation:scroll {loop / 15:.1f}s linear infinite}}
 .steam {{animation:rise 3s ease-out infinite}}
 .led {{animation:blink 2.4s step-end infinite}}
}}
{chr(10).join(keyframes)}
@keyframes caret {{0%,67% {{opacity:0}} 68%,93% {{opacity:1}} 94%,100% {{opacity:0}}}}
@keyframes blink {{50% {{opacity:0}}}}
@keyframes scroll {{from {{transform:translateY(0)}} to {{transform:translateY(-{loop}px)}}}}
@keyframes rise {{0% {{transform:translateY(8px);opacity:0}} 30% {{opacity:.7}} 100% {{transform:translateY(-22px);opacity:0}}}}
</style>
<defs>
<clipPath id="card"><rect width="{w}" height="{h}" rx="12"/></clipPath>
<clipPath id="screen"><rect x="48" y="48" width="336" height="178"/></clipPath>
<clipPath id="stream"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}"/></clipPath>
<linearGradient id="fade-top" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
<linearGradient id="fade-bottom" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
</defs>
<g clip-path="url(#card)" shape-rendering="crispEdges">
<rect width="{w}" height="{h}" fill="{BG}"/>
{stream}
<rect x="0" y="262" width="{w}" height="8" fill="#484456"/>
<rect x="0" y="270" width="{w}" height="50" fill="#292633"/>
<rect x="0" y="270" width="{w}" height="2" fill="#1C1A24"/>
<rect x="200" y="238" width="32" height="14" fill="#484456"/>
<path d="M40 36H392V40H396V238H36V40H40Z" fill="{ACCENT}"/>
<rect x="40" y="40" width="352" height="194" fill="#242232"/>
<rect x="48" y="48" width="336" height="178" fill="{BG}"/>
<rect class="led" x="376" y="229" width="8" height="3" fill="#C5BCFF"/>
<g clip-path="url(#screen)">
{chr(10).join(text)}
{chr(10).join(covers)}
<g class="caret-group">{prompt}<rect class="caret" x="{caret_x:.1f}" y="{caret_y}" width="9" height="18" fill="{ACCENT}"/></g>
</g>
<rect x="92" y="250" width="268" height="12" fill="#484456"/>
<rect x="92" y="250" width="268" height="2" fill="#5A566A"/>
{keys}
{sprite(MUG, 420, 230, 4)}
{steam}
{sprite(PLANT, 580, 222, 4)}
</g>
</svg>
'''


def pulse():
    return ('<style>@media (prefers-reduced-motion: no-preference) {svg {animation:pulse 2s ease-in-out infinite}}'
            '@keyframes pulse {0%,100% {opacity:1} 50% {opacity:.45}}</style>')


if __name__ == "__main__":
    assets = ROOT / "assets"
    (assets / "pixel").mkdir(parents=True, exist_ok=True)
    files = {"desk.svg": desk()}
    for name, art in ICONS.items():
        files[f"pixel/{name}.svg"] = icon(art, name.replace("-", " "), 24,
                                          pulse() if name == "dot-now" else "")
    for name, content in files.items():
        (assets / name).write_text(content, encoding="utf-8")
        print(f"Generated assets/{name}")
