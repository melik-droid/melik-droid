"""Update the activity card from GitHub's GraphQL API.

Needs GH_TOKEN (the workflow's token is enough). Failures leave the last card
intact. Counts are GitHub's own contribution numbers for the last 12 months.
"""

from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
USER = "melik-droid"
ACCENT, INK, MUTED, FAINT = "#9EB1FF", "#EDEEF0", "#B0B4BA", "#363A3F"

QUERY = """query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $cursor) {
      nodes { stargazerCount }
      pageInfo { hasNextPage endCursor }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def graphql(variables):
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN is required for the GraphQL API")
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    request = Request("https://api.github.com/graphql", data=body, method="POST",
                      headers={"Authorization": f"Bearer {token}", "User-Agent": "melik-profile",
                               "Content-Type": "application/json"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GraphQL error"))
    return payload["data"]


def collect(fetch=graphql):
    stars, cursor, contributions = 0, None, None
    while True:
        user = fetch({"login": USER, "cursor": cursor})["user"]
        contributions = contributions or user["contributionsCollection"]
        repos = user["repositories"]
        stars += sum(repo["stargazerCount"] for repo in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    calendar = contributions["contributionCalendar"]
    days = [(day["date"], day["contributionCount"])
            for week in calendar["weeks"] for day in week["contributionDays"]]
    weekly = [sum(day["contributionCount"] for day in week["contributionDays"]) for week in calendar["weeks"]]
    current, longest = streaks(days)
    return {"total": calendar["totalContributions"], "commits": contributions["totalCommitContributions"],
            "prs": contributions["totalPullRequestContributions"],
            "reviews": contributions["totalPullRequestReviewContributions"],
            "stars": stars, "current": current, "longest": longest, "weekly": weekly,
            "first": days[0][0] if days else None}


def streaks(days):
    """Current and longest run of active days. A quiet today doesn't break the streak yet."""
    counts = [count for _, count in sorted(days)]
    longest = run = 0
    for count in counts:
        run = run + 1 if count else 0
        longest = max(longest, run)
    if counts and counts[-1] == 0:
        counts = counts[:-1]
    current = 0
    for count in reversed(counts):
        if not count:
            break
        current += 1
    return current, longest


def plural(value, word):
    return f"{value:,} {word}{'' if value == 1 else 's'}"


def render(stats, updated):
    weekly = stats["weekly"] or [0]
    peak = max(weekly) or 1
    step = 432 / len(weekly)
    bars = []
    for index, count in enumerate(weekly):
        height = max(2, 64 * count / peak) if count else 2
        colour = ACCENT if count else FAINT
        bars.append(f'<rect x="{24 + index * step:.2f}" y="{206 - height:.2f}" width="{max(step - 2, 1):.2f}" '
                    f'height="{height:.2f}" fill="{colour}"/>')
    start = ""
    if stats["first"]:
        start = datetime.strptime(stats["first"], "%Y-%m-%d").strftime("%b %Y")
    tiles = [(f'{stats["commits"]:,}', "commits"), (f'{stats["prs"]:,}', "pull requests"),
             (f'{stats["reviews"]:,}', "code reviews"), (f'{stats["stars"]:,}', "stars"),
             (plural(stats["current"], "day"), "current streak"), (plural(stats["longest"], "day"), "longest streak")]
    tile_markup = []
    for index, (value, label) in enumerate(tiles):
        x, y = 24 + (index % 3) * 148, 272 + (index // 3) * 64
        tile_markup.append(f'<text x="{x}" y="{y}" fill="{INK}" font-size="22" font-weight="700">{escape(value)}</text>'
                           f'<text x="{x}" y="{y + 22}" fill="{MUTED}" font-size="13">{label}</text>')
    summary = (f'{plural(stats["total"], "contribution")} in the last year: {plural(stats["commits"], "commit")}, '
               f'{plural(stats["prs"], "pull request")}, {plural(stats["reviews"], "review")}, '
               f'{plural(stats["stars"], "star")}. Current streak {plural(stats["current"], "day")}, '
               f'longest {plural(stats["longest"], "day")}.')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="428" viewBox="0 0 480 428" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity</title>
<desc id="desc">{escape(summary)}</desc>
<rect width="480" height="428" rx="12" fill="#111113"/>
<g font-family="Arial,Helvetica,sans-serif">
<text x="24" y="38" fill="{INK}" font-size="22" font-weight="700">GitHub activity</text>
<text x="24" y="63" fill="{MUTED}" font-size="14">last 12 months · contributions per week</text>
<text x="24" y="118" fill="{INK}" font-size="44" font-weight="700">{stats["total"]:,}</text>
<text x="{36 + len(f'{stats["total"]:,}') * 25}" y="118" fill="{MUTED}" font-size="16">contributions</text>
<g shape-rendering="crispEdges">{"".join(bars)}</g>
<text x="24" y="226" fill="{MUTED}" font-size="12">{escape(start)}</text>
<text x="456" y="226" text-anchor="end" fill="{MUTED}" font-size="12">this week</text>
{"".join(tile_markup)}
<text x="24" y="407" fill="{MUTED}" font-size="13">Updated {escape(updated)} · refreshed daily</text>
</g>
</svg>
'''


if __name__ == "__main__":
    stats = collect()
    svg = render(stats, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    target = ROOT / "assets" / "stats.svg"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(target)
    print(f"Updated activity card: {stats['total']} contributions, {stats['stars']} stars")
