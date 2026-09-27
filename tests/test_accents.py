import unittest
import xml.etree.ElementTree as ET

from scripts.generate_accents import ticker
from scripts.generate_scene import CODE, CODE_CHAR, desk, highlight
from scripts.pixel import ICONS, MUG, PLANT, sprite


class PixelTests(unittest.TestCase):
    def test_runs_merge_and_transparency(self):
        self.assertEqual(sprite(["PP.P"]).count("<rect"), 2)
        self.assertEqual(sprite(["...."]), "")

    def test_ragged_sprite_is_rejected(self):
        with self.assertRaises(ValueError):
            sprite(["PP", "P"])

    def test_every_sprite_is_rectangular_with_known_colours(self):
        for name, art in {**ICONS, "mug": MUG, "plant": PLANT}.items():
            with self.subTest(name):
                sprite(art)


class SvgTests(unittest.TestCase):
    def test_generated_svgs_parse(self):
        for svg in [desk(), ticker(880), ticker(440)]:
            ET.fromstring(svg)

    def test_code_stream_fits_and_highlights(self):
        self.assertTrue(all(len(line) * CODE_CHAR <= 212 for line in CODE))
        marked = highlight('model = YOLO("ppe.pt") & <x>')
        self.assertIn('fill="#9DBAA5">&quot;ppe.pt&quot;', marked)
        self.assertIn("&amp;", marked)
        ET.fromstring(f"<text>{marked}</text>")


if __name__ == "__main__":
    unittest.main()
