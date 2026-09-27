import unittest
import xml.etree.ElementTree as ET

from scripts.update_stats import collect, render, streaks


def page(stars, has_next, cursor=None, days=()):
    return {"user": {
        "repositories": {"nodes": [{"stargazerCount": s} for s in stars],
                         "pageInfo": {"hasNextPage": has_next, "endCursor": cursor}},
        "contributionsCollection": {
            "totalCommitContributions": 40, "totalPullRequestContributions": 5,
            "totalPullRequestReviewContributions": 2,
            "contributionCalendar": {"totalContributions": sum(c for _, c in days), "weeks": [
                {"contributionDays": [{"date": d, "contributionCount": c} for d, c in days[:3]]},
                {"contributionDays": [{"date": d, "contributionCount": c} for d, c in days[3:]]}]}}}}


DAYS = [("2026-09-21", 1), ("2026-09-22", 0), ("2026-09-23", 2),
        ("2026-09-24", 3), ("2026-09-25", 1), ("2026-09-26", 4), ("2026-09-27", 0)]


class StreakTests(unittest.TestCase):
    def test_quiet_today_keeps_streak(self):
        self.assertEqual(streaks(DAYS), (4, 4))

    def test_active_today_counts(self):
        self.assertEqual(streaks(DAYS[:-1] + [("2026-09-27", 1)]), (5, 5))

    def test_broken_streak(self):
        self.assertEqual(streaks([("2026-09-25", 2), ("2026-09-26", 0), ("2026-09-27", 0)]), (0, 1))

    def test_unsorted_and_empty(self):
        self.assertEqual(streaks(list(reversed(DAYS))), (4, 4))
        self.assertEqual(streaks([]), (0, 0))


class CollectTests(unittest.TestCase):
    def test_stars_paginate_and_calendar_is_read_once(self):
        cursors = []
        def fetch(variables):
            cursors.append(variables["cursor"])
            return page([3, 1], True, "abc", DAYS) if variables["cursor"] is None else page([2], False, days=[])
        stats = collect(fetch)
        self.assertEqual(cursors, [None, "abc"])
        self.assertEqual(stats["stars"], 6)
        self.assertEqual(stats["total"], 11)
        self.assertEqual(stats["weekly"], [3, 8])
        self.assertEqual((stats["current"], stats["longest"]), (4, 4))
        self.assertEqual(stats["first"], "2026-09-21")

    def test_api_failure_propagates(self):
        def fail(_):
            raise RuntimeError("rate limited")
        with self.assertRaises(RuntimeError):
            collect(fail)


class RenderTests(unittest.TestCase):
    def test_svg_is_valid_and_singular_days(self):
        stats = collect(lambda v: page([1], False, days=DAYS))
        stats["current"] = 1
        svg = render(stats, "2026-09-27")
        ET.fromstring(svg)
        self.assertIn("1 day", svg)
        self.assertIn("4 days", svg)

    def test_no_activity(self):
        stats = {"total": 0, "commits": 0, "prs": 0, "reviews": 0, "stars": 0,
                 "current": 0, "longest": 0, "weekly": [], "first": None}
        ET.fromstring(render(stats, "2026-09-27"))


if __name__ == "__main__":
    unittest.main()
