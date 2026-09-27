import unittest
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlsplit

from scripts.update_languages import collect, eligible, render, segments


def repo(name, **extra):
    return dict(name=name, owner={"login": "melik-droid"}, **extra)


class LanguageTests(unittest.TestCase):
    def test_excludes_forks_private_profile_and_other_owners(self):
        for item in [repo("x", fork=True), repo("x", private=True), repo("MELIK-DROID"),
                     {"name": "x", "owner": {"login": "someone-else"}}]:
            self.assertFalse(eligible(item))
        self.assertTrue(eligible(repo("code")))

    def test_pagination_aggregation_and_empty_repos(self):
        calls = []
        def fetch(path):
            calls.append(path)
            page = parse_qs(urlsplit(path).query).get("page", [None])[0]
            if page == "1":
                return [repo("fork", fork=True)] * 99 + [repo("one")]
            if page == "2":
                return [repo("two"), repo("empty")]
            return {"Python": 75, "C": 25} if "/one/" in path else ({"C": 100} if "/two/" in path else {})
        totals, count = collect(fetch)
        self.assertEqual(totals, {"Python": 75, "C": 125})
        self.assertEqual(count, 2)
        self.assertEqual(len(calls), 5)

    def test_api_failure_is_not_silently_partial(self):
        def fail(_):
            raise RuntimeError("rate limited")
        with self.assertRaises(RuntimeError):
            collect(fail)

    def test_build_and_document_bytes_are_excluded(self):
        def fetch(path):
            return [repo("code")] if "?" in path else {"Python": 10, "Makefile": 900, "TeX": 50, "CSS": 20}
        self.assertEqual(collect(fetch), ({"Python": 10}, 1))

    def test_other_preserves_total(self):
        totals = {f"lang{i}": i for i in range(1, 11)}
        parts = segments(totals)
        self.assertEqual(len(parts), 7)
        self.assertEqual(parts[-1][0], "Other")
        self.assertEqual(sum(v for _, v in parts), sum(totals.values()))

    def test_empty_and_escaped_svg(self):
        for totals in [{}, {"C<&": 1}]:
            ET.fromstring(render(totals, 1, "2026-09-27"))
        self.assertIn("No language data", render({}, 0, "2026-09-27"))


if __name__ == "__main__":
    unittest.main()
