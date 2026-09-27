"""Pixel-art helpers and sprites shared by the profile generators.

Sprites are lists of equal-length strings. "." is transparent; every other
character is a key into a palette. Runs of the same colour on a row are merged
into one rect so the SVGs stay small.
"""

BG, INK, MUTED, ACCENT = "#0D0D0F", "#EDEDEF", "#A1A1AA", "#9391FF"

PALETTE = {
    "P": ACCENT,     # purple
    "L": "#B1AEFF",  # lavender
    "W": "#C5BCFF",  # highlight
    "D": "#484456",  # desk / metal
    "K": "#292633",  # shadow
    "G": "#77748F",  # muted grey
    "S": "#242232",  # bezel
    "B": BG,         # screen black
    "I": INK,        # white-ish
    "V": "#9DBAA5",  # sage leaves
}


def num(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def sprite(art, x=0, y=0, px=1, palette=PALETTE):
    width = len(art[0])
    rects = []
    for row, line in enumerate(art):
        if len(line) != width:
            raise ValueError(f"sprite row {row} is {len(line)} wide, expected {width}")
        col = 0
        while col < width:
            key = line[col]
            end = col + 1
            while end < width and line[end] == key:
                end += 1
            if key != ".":
                rects.append(f'<rect x="{num(x + col * px)}" y="{num(y + row * px)}" '
                             f'width="{num((end - col) * px)}" height="{num(px)}" fill="{palette[key]}"/>')
            col = end
    return "".join(rects)


def icon(art, title, size=24, extra=""):
    """A standalone square icon, drawn at one SVG unit per pixel."""
    w, h = len(art[0]), len(art)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size * h // w}" '
            f'viewBox="0 0 {w} {h}" shape-rendering="crispEdges" role="img" aria-label="{title}">'
            f'{extra}{sprite(art)}</svg>\n')


ICONS = {
    "briefcase": [
        "............",
        "....PPPP....",
        "....P..P....",
        ".PPPPPPPPPP.",
        ".PLLLLLLLLP.",
        ".PLLLLLLLLP.",
        ".PPPPWWPPPP.",
        ".PLLLWWLLLP.",
        ".PLLLLLLLLP.",
        ".PLLLLLLLLP.",
        ".PPPPPPPPPP.",
        "............",
    ],
    "gear": [
        ".....PP.....",
        ".P..PPPP..P.",
        "..PPPPPPPP..",
        "..PPPLLPPP..",
        ".PPPL..LPPP.",
        "PPPL....LPPP",
        "PPPL....LPPP",
        ".PPPL..LPPP.",
        "..PPPLLPPP..",
        "..PPPPPPPP..",
        ".P..PPPP..P.",
        ".....PP.....",
    ],
    "chart": [
        "............",
        "........LL..",
        "........LL..",
        "........LL..",
        ".....PP.LL..",
        ".....PP.LL..",
        ".....PP.LL..",
        "..PP.PP.LL..",
        "..PP.PP.LL..",
        "..PP.PP.LL..",
        "GGGGGGGGGGGG",
        "............",
    ],
    "dot": [
        "..GGGG..",
        ".GKKKKG.",
        "GKKKKKKG",
        "GKKKKKKG",
        "GKKKKKKG",
        "GKKKKKKG",
        ".GKKKKG.",
        "..GGGG..",
    ],
    "dot-now": [
        "..PPPP..",
        ".PLLLLP.",
        "PLWWLLLP",
        "PLWLLLLP",
        "PLLLLLLP",
        "PLLLLLLP",
        ".PLLLLP.",
        "..PPPP..",
    ],
}

MUG = [
    ".PPPPP..",
    ".PKKKP..",
    ".PLLLPPP",
    ".PLLLP.P",
    ".PLLLP.P",
    ".PLLLPPP",
    ".PLLLP..",
    "..PPP...",
]

PLANT = [
    "....V.....",
    "...VV.V...",
    ".V.VVVV...",
    ".VVVVV.VV.",
    "..VVVVVV..",
    "...VVVV...",
    "....VV....",
    "..DDDDDD..",
    "..DGGGGD..",
    "...DDDD...",
]
