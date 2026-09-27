"""Update the language card from public, owned, non-fork GitHub repositories.

Uses the standard library and optional GH_TOKEN. Failures leave the last card
intact. Counts bytes reported by GitHub Linguist, not proficiency or commits.
"""

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
USER = "melik-droid"
COLORS = ["#9391FF", "#B1AEFF", "#7088CF", "#6CA5B8", "#9DBAA5", "#B2A0C4", "#777780"]
# Keep the card focused on programming, not stylesheets, documents or build files.
EXCLUDED = {"Makefile", "CMake", "Dockerfile", "HTML", "CSS", "SCSS", "Sass", "Less",
            "TeX", "Markdown", "MDX", "JSON", "YAML", "XML"}


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "melik-profile",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request("https://api.github.com" + path, headers=headers), timeout=30) as response:
        return json.load(response)


def eligible(repo):
    return (not repo.get("fork", False) and not repo.get("private", False)
            and repo["name"].casefold() != USER.casefold()
            and repo["owner"]["login"].casefold() == USER.casefold())


def collect(fetch=api):
    totals, count, page = Counter(), 0, 1
    while True:
        repos = fetch(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        for repo in repos:
            if eligible(repo):
                languages = {name: size for name, size in
                             fetch(f"/repos/{USER}/{repo['name']}/languages").items()
                             if name not in EXCLUDED}
                if sum(languages.values()) > 0:
                    totals.update(languages)
                    count += 1
        if len(repos) < 100:
            break
        page += 1
    return totals, count


def segments(totals):
    items = sorted(((name, size) for name, size in totals.items() if size > 0),
                   key=lambda item: (-item[1], item[0]))
    if len(items) > 7:
        items = items[:6] + [("Other", sum(size for _, size in items[6:]))]
    return items


def render(totals, count, date):
    items = segments(totals)
    total = sum(size for _, size in items)
    height = 162 + max(len(items), 1) * 38
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" viewBox="0 0 480 {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Languages across my public repos</title>',
           '<desc id="desc">Code bytes reported by GitHub. Excludes forks, private repositories and the profile repository. Not a proficiency score.</desc>',
           f'<rect width="480" height="{height}" rx="12" fill="#0D0D0F"/>',
           '<g font-family="Arial,Helvetica,sans-serif">',
           '<text x="24" y="38" fill="#EDEDEF" font-size="22" font-weight="700">Languages in my repos</text>',
           f'<text x="24" y="63" fill="#A1A1AA" font-size="14">{count} public source repos · code bytes</text>']
    x = 24.0
    for index, (name, size) in enumerate(items):
        color = COLORS[index]
        width = 432 * size / total
        out.append(f'<rect x="{x:.3f}" y="84" width="{width:.3f}" height="12" fill="{color}"/>')
        x += width
        y = 130 + index * 38
        percent = size / total * 100
        label = f"{percent:.1f}%" if percent >= .1 else "&lt;0.1%"
        out.extend([f'<circle cx="30" cy="{y - 6}" r="5" fill="{color}"/>',
                    f'<text x="46" y="{y}" fill="#EDEDEF" font-size="19">{escape(name)}</text>',
                    f'<text x="456" y="{y}" text-anchor="end" fill="#A1A1AA" font-size="19">{label}</text>'])
    if not items:
        out.append('<text x="24" y="130" fill="#A1A1AA" font-size="18">No language data available yet.</text>')
    out.append(f'<text x="24" y="{height - 21}" fill="#A1A1AA" font-size="13">Updated {escape(date)} · refreshed daily</text></g></svg>\n')
    return "\n".join(out)


if __name__ == "__main__":
    totals, count = collect()
    svg = render(totals, count, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    target = ROOT / "assets" / "languages.svg"
    target.parent.mkdir(exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(target)
    print(f"Updated language card from {count} public repositories")
