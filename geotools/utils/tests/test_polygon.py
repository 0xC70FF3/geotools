import geohash

from unittest import TestCase
from unittest import main

from geotools.utils.polygon import Polygon


class GeoHashTestCase(TestCase):
    """polygon: [(2.32378006, 48.86403720), (2.35691071, 48.88616602),  (2.37905502, 48.85816465)]
       | out     | u09wj5 | ((2.3291015625, 48.8836669921875), (2.340087890625, 48.88916015625))  |
       | partial | u09tvy | ((2.362060546875, 48.856201171875), (2.373046875, 48.8616943359375))  |
       | "       | u09tvz | ((2.362060546875, 48.8616943359375), (2.373046875, 48.8671875))       |
       | "       | u09wj0 | ((2.3291015625, 48.8671875), (2.340087890625, 48.8726806640625))      |
       | in      | u09wj2 | ((2.340087890625, 48.8671875), (2.35107421875, 48.8726806640625))     |
       | edge    | u09wje | ((2.362060546875, 48.88916015625), (2.35107421875, 48.8836669921875)) |
    """
    def setUp(self):
        self.polygon = Polygon([
            (2.32378006, 48.86403720),
            (2.35691071, 48.88616602),
            (2.37905502, 48.85816465)])

    def test_bbox(self):
        self.assertDictEqual({
                "w": 2.32378006,
                "s": 48.85816465,
                "e": 2.37905502,
                "n": 48.88616602,
            },
            self.polygon.bbox()
        )

    def test_contains(self):
        u09wj5 = geohash.bbox("u09wj5")
        u09wj2 = geohash.bbox("u09wj2")
        self.assertFalse(self.polygon.contains((u09wj5["w"], u09wj5["s"])))  # sw of u09wj5
        self.assertTrue(self.polygon.contains((u09wj2["w"], u09wj2["s"])))  # sw of u09wj2
        self.assertTrue(self.polygon.contains(self.polygon._coordinates[0]))  # first point of polygon

    def test_intersects(self):
        bboxes = {
            "u09wj5": False,  # out
            "u09tvy": True,  # partially in
            "u09tvz": True,  # partially in
            "u09wj0": True,  # partially in
            "u09wj2": False,  # in
            "u09wje": True,  # edge crosses
        }
        for hashcode, expected in bboxes.items():
            bbox = geohash.bbox(hashcode)
            self.assertEqual(expected, self.polygon.intersects(bbox))

    def test_filter(self):
        hashes_to_be_checked = [
            "u09wj5",  # out
            "u09tvy",  # partially in
            "u09tvz",  # partially in
            "u09wj0",  # partially in
            "u09wj2",  # in
            "u09wje",  # edge crosses
        ]
        inside, partially_inside = self.polygon._filter(hashes_to_be_checked)
        self.assertEqual(["u09wj2"], inside)
        self.assertEqual(128, len(partially_inside))
        for hashcode in partially_inside:
            self.assertTrue(
                hashcode.startswith("u09tvy") or
                hashcode.startswith("u09tvz") or
                hashcode.startswith("u09wj0") or
                hashcode.startswith("u09wje")
            )

    def test_filter_with_englobing_bbox(self):
        inside, partially_inside = self.polygon._filter(["u09"])
        self.assertEqual([], inside)
        self.assertEqual(32, len(partially_inside))
        for hashcode in partially_inside:
            self.assertTrue(hashcode.startswith("u09"))

    def test_hashes(self):
        self.assertListEqual(
            ['u09tvx', 'u09wj2', 'u09wj8', 'u09wj9'],
            self.polygon.hashcodes(min_precision=2, max_precision=6))
        self.assertListEqual(
            ['u09tvx', 'u09wj2', 'u09wj8', 'u09wj9'],
            self.polygon.hashcodes(min_precision=6, max_precision=6))

        hashcodes = self.polygon.hashcodes(min_precision=3, max_precision=7)
        self.assertEqual(190, len(hashcodes))
        self.assertTrue({'u09tvx', 'u09wj2', 'u09wj8', 'u09wj9'}.issubset(hashcodes))
        for hashcode in hashcodes:
            self.assertTrue(hashcode.startswith("u09"))

        hashcodes = self.polygon.hashcodes(min_precision=3, max_precision=9)
        self.assertEqual(10149, len(hashcodes))
        self.assertTrue({'u09tvx', 'u09wj2', 'u09wj8', 'u09wj9'}.issubset(hashcodes))
        for hashcode in hashcodes:
            self.assertTrue(hashcode.startswith("u09"))


if __name__ == '__main__':
    main()


