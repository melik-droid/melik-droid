"""Update the "On repeat" card from Last.fm.

Needs LASTFM_API_KEY. Without it the script skips and the last card stays.
Failures also leave the last card intact. The key is never printed.
"""

from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
USER = "melik_cymz"
ACCENT, INK, MUTED, FAINT = "#9391FF", "#EDEDEF", "#A1A1AA", "#2B2B35"


def lastfm(method, **params):
    query = urlencode({"method": method, "user": USER, "api_key": os.environ["LASTFM_API_KEY"],
                       "format": "json", **params})
    request = Request(f"https://ws.audioscrobbler.com/2.0/?{query}", headers={"User-Agent": "melik-profile"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "error" in payload:
        raise RuntimeError(f"Last.fm error {payload['error']}: {payload.get('message', '')}")
    return payload


def as_list(value):
    """Last.fm returns a bare object instead of a list when there is one item."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def collect(fetch=lastfm):
    recent = as_list(fetch("user.getrecenttracks", limit=1)["recenttracks"].get("track"))
    top = as_list(fetch("user.gettopartists", period="7day", limit=5)["topartists"].get("artist"))
    last = None
    if recent:
        track = recent[0]
        last = {"track": track["name"], "artist": track["artist"].get("#text") or track["artist"].get("name", "")}
    artists = [(artist["name"], int(artist["playcount"])) for artist in top]
    return {"last": last, "artists": artists}


def clip(text, limit):
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def vinyl(x, y, r=44):
    grooves = "".join(f'<circle cx="{x}" cy="{y}" r="{g}" fill="none" stroke="#2B2B35"/>'
                      for g in (r * .82, r * .66, r * .5))
    return (f'<g class="vinyl"><circle cx="{x}" cy="{y}" r="{r}" fill="#17151F"/>{grooves}'
            f'<path d="M{x} {y - r}A{r} {r} 0 0 1 {x + r} {y}" fill="none" stroke="#3B354E" stroke-width="4"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * .27:.1f}" fill="{ACCENT}"/><circle cx="{x}" cy="{y}" r="3" fill="#0D0D0F"/></g>')


def render(music, updated):
    """A 640x320 card, the same shape as the desk scene so they sit side by side."""
    last, artists = music["last"], music["artists"]
    out = []
    if last:
        out.append(f'<text x="28" y="222" fill="{MUTED}" font-size="14">LAST PLAYED</text>'
                   f'<text x="28" y="250" fill="{INK}" font-size="21" font-weight="700">{escape(clip(last["track"], 22))}</text>'
                   f'<text x="28" y="274" fill="{MUTED}" font-size="17">{escape(clip(last["artist"], 26))}</text>')
    else:
        out.append(f'<text x="28" y="238" fill="{MUTED}" font-size="17">Waiting for the</text>'
                   f'<text x="28" y="262" fill="{MUTED}" font-size="17">first Last.fm sync.</text>')
    out.append(f'<line x1="318" y1="72" x2="318" y2="288" stroke="{FAINT}"/>'
               f'<text x="344" y="92" fill="{MUTED}" font-size="14">TOP ARTISTS · 7 DAYS</text>')
    peak = max((plays for _, plays in artists), default=1) or 1
    for index, (name, plays) in enumerate(artists):
        y = 126 + index * 36
        width = max(4, 268 * plays / peak)
        out.append(f'<text x="344" y="{y}" fill="{INK}" font-size="18">{escape(clip(name, 17))}</text>'
                   f'<text x="612" y="{y}" text-anchor="end" fill="{MUTED}" font-size="15">{plays:,} plays</text>'
                   f'<rect x="344" y="{y + 8}" width="268" height="5" fill="{FAINT}"/>'
                   f'<rect x="344" y="{y + 8}" width="{width:.2f}" height="5" fill="{ACCENT}"/>')
    if last and not artists:
        out.append(f'<text x="344" y="126" fill="{MUTED}" font-size="17">Nothing scrobbled this week.</text>')
    summary = "Top artists this week: " + (", ".join(f"{n} ({p} plays)" for n, p in artists) or "none")
    if last:
        summary = f'Last played {last["track"]} by {last["artist"]}. ' + summary
    footer = f"Updated {escape(updated)} · refreshed daily" if updated else "First sync pending"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="320" viewBox="0 0 640 320" role="img" aria-labelledby="title desc">
<title id="title">On repeat</title>
<desc id="desc">{escape(summary)}</desc>
<style>
.vinyl {{transform-box:fill-box;transform-origin:center}}
@media (prefers-reduced-motion: no-preference) {{ .vinyl {{animation:spin 4s linear infinite}} }}
@keyframes spin {{to {{transform:rotate(360deg)}}}}
</style>
<rect width="640" height="320" rx="12" fill="#0D0D0F"/>
<g font-family="Arial,Helvetica,sans-serif">
<text x="28" y="46" fill="{INK}" font-size="26" font-weight="700">On repeat</text>
<text x="612" y="46" text-anchor="end" fill="{MUTED}" font-size="16">last.fm/user/{USER}</text>
{vinyl(88, 140)}
{"".join(out)}
<text x="28" y="304" fill="{MUTED}" font-size="14">{footer}</text>
</g>
</svg>
'''


def write(svg):
    target = ROOT / "assets" / "music.svg"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(target)


if __name__ == "__main__":
    if not os.environ.get("LASTFM_API_KEY"):
        if not (ROOT / "assets" / "music.svg").exists():
            write(render({"last": None, "artists": []}, None))
        print("LASTFM_API_KEY is not set; keeping the current music card")
        raise SystemExit(0)
    music = collect()
    write(render(music, datetime.now(timezone.utc).strftime("%Y-%m-%d")))
    print(f"Updated music card with {len(music['artists'])} artists")
