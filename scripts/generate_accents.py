"""Generate original animated SVG accents and contact badges, without dependencies."""

from html import escape
from pathlib import Path

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


def computer():
    rain = []
    for i in range(8):
        x = 15 + i * 27
        rain.append(f'<g class="rain" style="animation-delay:-{i * .7}s" opacity=".25">'
                    f'<text x="{x}" y="12">01</text><text x="{x}" y="30">10</text>'
                    f'<text x="{x}" y="48">01</text></g>')
    keys = ''.join(f'<rect x="{44 + col * 13 - row * 3}" y="{134 + row * 7}" width="9" height="3" fill="#77748F"/>'
                   for row in range(3) for col in range(11))
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="190" viewBox="0 0 240 190" role="img" aria-labelledby="title desc">
<title id="title">A little computer, always building</title>
<desc id="desc">An original purple pixel laptop with falling binary digits and a blinking terminal cursor.</desc>
<style>
text {font-family:'Courier New',monospace;font-size:10px;fill:#9391FF}
@media (prefers-reduced-motion: no-preference) {
 .rain {animation:fall 5s linear infinite}
 .caret {animation:blink 1s step-end infinite}
 .code {animation:code 5s steps(5,end) infinite}
}
@keyframes fall {from {transform:translateY(-45px);opacity:0} 20% {opacity:.3} to {transform:translateY(115px);opacity:0} }
@keyframes blink {50% {opacity:0}}
@keyframes code {0%,100% {opacity:.45} 50% {opacity:1}}
</style>
<rect width="240" height="190" rx="12" fill="#0D0D0F"/>
''' + ''.join(rain) + '''
<g shape-rendering="crispEdges">
<path d="M44 42H196V48H202V122H38V48H44Z" fill="#9391FF"/>
<path d="M47 50H193V114H47Z" fill="#242232"/>
<path d="M54 57H186V107H54Z" fill="#0D0D0F"/>
<path d="M38 122H202L222 159V165H18V159Z" fill="#484456"/>
<path d="M38 126H202L218 156H22Z" fill="#292633"/>
''' + keys + '''
<path d="M97 155H145V158H97Z" fill="#B1AEFF"/>
<path d="M18 159H222V165H18Z" fill="#9391FF"/>
<rect x="181" y="118" width="4" height="2" fill="#C5BCFF"/>
</g>
<text x="61" y="72" font-size="9">melik@dev ~</text>
<text x="61" y="87">&gt; build</text>
<rect class="caret" x="109" y="79" width="5" height="9" fill="#9391FF"/>
<g class="code" fill="#77748F"><rect x="61" y="95" width="43" height="2"/><rect x="110" y="95" width="21" height="2"/><rect x="136" y="95" width="31" height="2"/></g>
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
    files = {"typing.svg": typing(), "computer.svg": computer(),
             "website.svg": badge("Website", "&lt;/&gt;", 108),
             "linkedin.svg": badge("LinkedIn", "in", 109),
             "email.svg": badge("Email", "@", 92)}
    for name, content in files.items():
        (assets / name).write_text(content, encoding="utf-8")
        print(f"Generated assets/{name}")
