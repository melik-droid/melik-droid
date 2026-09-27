import unittest
import xml.etree.ElementTree as ET

from scripts.update_music import as_list, clip, collect, render


def fake(recent, top):
    def fetch(method, **_):
        if method == "user.getrecenttracks":
            return {"recenttracks": {"track": recent}}
        return {"topartists": {"artist": top}}
    return fetch


class MusicTests(unittest.TestCase):
    def test_single_items_arrive_as_objects(self):
        music = collect(fake({"name": "Song", "artist": {"#text": "Band"}},
                             {"name": "Band", "playcount": "12"}))
        self.assertEqual(music, {"last": {"track": "Song", "artist": "Band"}, "artists": [("Band", 12)]})

    def test_now_playing_list_uses_first_track(self):
        recent = [{"name": "Now", "artist": {"#text": "A"}, "@attr": {"nowplaying": "true"}},
                  {"name": "Before", "artist": {"#text": "B"}}]
        self.assertEqual(collect(fake(recent, []))["last"]["track"], "Now")

    def test_empty_account(self):
        self.assertEqual(collect(fake([], [])), {"last": None, "artists": []})
        self.assertEqual(as_list(None), [])

    def test_api_error_propagates(self):
        def fail(*_, **__):
            raise RuntimeError("Last.fm error 10: Invalid API key")
        with self.assertRaises(RuntimeError):
            collect(fail)

    def test_render_escapes_and_clips(self):
        music = {"last": {"track": "<Tom & Jerry>" * 5, "artist": "A&B"},
                 "artists": [("Sigur Rós & <friends>", 30), ("Two", 0)]}
        svg = render(music, "2026-09-27")
        ET.fromstring(svg)
        self.assertIn("…", svg)
        self.assertEqual(len(clip("x" * 50, 22)), 22)

    def test_placeholder(self):
        svg = render({"last": None, "artists": []}, None)
        ET.fromstring(svg)
        self.assertIn("First sync pending", svg)


if __name__ == "__main__":
    unittest.main()
