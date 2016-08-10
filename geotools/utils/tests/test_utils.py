import math

from unittest import TestCase
from unittest import main

from geotools.utils import *


class UtilsTestCase(TestCase):

    def setUp(self):
        self.sydney = (151.206146, -33.872796)
        self.buenos_aires = (-58.380449, -34.602875)
        self.new_york = (-74.011237, 40.721119)
        self.amsterdam = (4.894252, 52.372103)
        self.berlin = (13.385721, 52.527109)
        self.london = (-0.123656, 51.51283)

    def test_validate(self):

        self.assertTrue(validate(0, 0))
        self.assertTrue(validate(-179.9, 0))
        self.assertTrue(validate(179.9, 0))
        self.assertTrue(validate(0, -89.9))
        self.assertTrue(validate(0, 89.9))

        try:
            assert validate(-181.0, 0)
            self.fail("should never be there...")
        except ValueError:
            pass

        try:
            assert validate(181.0, 0)
            self.fail("should never be there...")
        except ValueError:
            pass

        try:
            assert validate(0, 91.0)
            self.fail("should never be there...")
        except ValueError:
            pass

        try:
            assert validate(0, -91.0)
            self.fail("should never be there...")
        except ValueError:
            pass

    def test_distance(self):
        d = distance(self.sydney, self.berlin)
        self.assertEqual(16100198, math.floor(d))

    def test_intersects(self):

        def assert_intersects(l1, l2, expected=True):
            self.assertEquals(expected, intersects(l1, l2))
            self.assertEquals(expected, intersects(l2, l1))
            self.assertEquals(expected, intersects((l1[1], l1[0]), (l2[1], l2[0])))
            self.assertEquals(expected, intersects((l2[1], l2[0]), (l1[1], l1[0])))

        assert_intersects(((1, 1), (2, 2)), ((2, 1), (1, 2)))
        assert_intersects(((1, 1), (2, 2)), ((2, 1), (3, 0)), expected=False)
        assert_intersects(((1, 1), (1, 4)), ((1, 2), (1, 3)))  # collinear
        assert_intersects(((1, 1), (1, 3)), ((1, 2), (1, 4)))  # collinear
        assert_intersects(((1, 0), (4, 0)), ((2, 0), (3, 0)))  # vertical
        assert_intersects(((0, 1), (0, 4)), ((0, 2), (0, 3)))  # horizontal
        assert_intersects(((1, 1), (2, 2)), ((3, 3), (4, 4)), expected=False)  # collinear
        assert_intersects(((1, 0), (2, 0)), ((3, 0), (4, 0)), expected=False)  # vertical
        assert_intersects(((0, 1), (0, 2)), ((0, 3), (0, 4)), expected=False)  # vertical

        # some extra cases
        assert_intersects(((0, 0), (-2, -1)), ((1, -1), (1, 1)), expected=False)
        assert_intersects(((0, 0), (-2, -1)), ((-1, -1), (-1, 1)))
        assert_intersects(((2, 2), (5, 2)), ((3, 1), (4, 1)), expected=False)

        # one edge of segment is on the other segment
        assert_intersects(((0, 0), (2, 2)), ((1, 1), (2, 0)))

    def test_is_west(self):
        self.assertTrue(is_west(1, 2))
        self.assertTrue(is_west(1, 180))
        self.assertFalse(is_west(1, 181))
        self.assertTrue(is_west(2, 181))

    def test_south(self):
        s = south(geohash.encode(self.london[1], self.london[0], 5))
        self.assertEqual("gcpuv", s)

    def test_north(self):
        n = north(geohash.encode(self.london[1], self.london[0], 5))
        self.assertEqual("gcpvm", n)

    def test_west(self):
        w = west(geohash.encode(self.london[1], self.london[0], 5))
        self.assertEqual("gcpvh", w)

    def test_east(self):
        e = east(geohash.encode(self.london[1], self.london[0], 5))
        self.assertEqual("gcpvn", e)

    def test_matches(self):
        self.assertTrue(matches(*self.london, "gcpvj1tgyx"))

    def test_subhashcodes(self):
        hashes = subhashcodes("gcpv")
        self.assertTrue({"gcpvj", "gcpvm", "gcpvh", "gcpvn"}.issubset(hashes))
        self.assertFalse({"gcpuv"}.issubset(hashes))
        for hashcode in hashes:
            self.assertTrue(hashcode.startswith("gcpv"))

    def test_adjacent(self):
        # north
        self.assertEqual("gz", adjacent("gy", 'n'))
        self.assertEqual("gy", adjacent("gv", 'n'))
        self.assertEqual("gv", adjacent("gu", 'n'))
        self.assertEqual("gu", adjacent("gg", 'n'))
        self.assertEqual("gg", adjacent("gf", 'n'))
        self.assertEqual("gf", adjacent("gc", 'n'))
        self.assertEqual("gc", adjacent("gb", 'n'))
        self.assertEqual("gb", adjacent("ez", 'n'))

        self.assertEqual(None, adjacent("gz", 'n'))

        self.assertEqual("e", adjacent("7", 'n'))
        self.assertEqual("e2", adjacent("7r", 'n'))
        self.assertEqual("e2h", adjacent("7ru", 'n'))
        self.assertEqual("e2h8", adjacent("7rux", 'n'))
        self.assertEqual("e2h85", adjacent("7ruxg", 'n'))

        self.assertEqual("e2hs5", adjacent("e2heg", 'n'))
        self.assertEqual("e2heg", adjacent("e2hee", 'n'))
        self.assertEqual("e2hee", adjacent("e2he7", 'n'))
        self.assertEqual("e2he7", adjacent("e2he5", 'n'))
        self.assertEqual("e2he5", adjacent("e2hdg", 'n'))

        # south
        self.assertEqual("gy", adjacent("gz", 's'))
        self.assertEqual("gv", adjacent("gy", 's'))
        self.assertEqual("gu", adjacent("gv", 's'))
        self.assertEqual("gg", adjacent("gu", 's'))
        self.assertEqual("gf", adjacent("gg", 's'))
        self.assertEqual("gc", adjacent("gf", 's'))
        self.assertEqual("gb", adjacent("gc", 's'))
        self.assertEqual("ez", adjacent("gb", 's'))

        self.assertEqual(None, adjacent("58", 's'))

        self.assertEqual("7", adjacent("e", 's'))
        self.assertEqual("7r", adjacent("e2", 's'))
        self.assertEqual("7ru", adjacent("e2h", 's'))
        self.assertEqual("7rux", adjacent("e2h8", 's'))
        self.assertEqual("7ruxg", adjacent("e2h85", 's'))

        self.assertEqual("e2heg", adjacent("e2hs5", 's'))
        self.assertEqual("e2hee", adjacent("e2heg", 's'))
        self.assertEqual("e2he7", adjacent("e2hee", 's'))
        self.assertEqual("e2he5", adjacent("e2he7", 's'))
        self.assertEqual("e2hdg", adjacent("e2he5", 's'))

        # east
        self.assertEqual("3", adjacent("2", 'e'))
        self.assertEqual("6", adjacent("3", 'e'))
        self.assertEqual("7", adjacent("6", 'e'))
        self.assertEqual("k", adjacent("7", 'e'))
        self.assertEqual("m", adjacent("k", 'e'))
        self.assertEqual("q", adjacent("m", 'e'))
        self.assertEqual("r", adjacent("q", 'e'))
        self.assertEqual("2", adjacent("r", 'e'))

        self.assertEqual("kn", adjacent("7y", 'e'))
        self.assertEqual("7y", adjacent("7w", 'e'))
        self.assertEqual("7w", adjacent("7q", 'e'))
        self.assertEqual("7q", adjacent("7n", 'e'))

        # west
        self.assertEqual("r", adjacent("2", 'w'))
        self.assertEqual("2", adjacent("3", 'w'))
        self.assertEqual("3", adjacent("6", 'w'))
        self.assertEqual("6", adjacent("7", 'w'))
        self.assertEqual("7", adjacent("k", 'w'))
        self.assertEqual("k", adjacent("m", 'w'))
        self.assertEqual("m", adjacent("q", 'w'))
        self.assertEqual("q", adjacent("r", 'w'))

        self.assertEqual("7w", adjacent("7y", 'w'))
        self.assertEqual("7q", adjacent("7w", 'w'))
        self.assertEqual("7n", adjacent("7q", 'w'))
        self.assertEqual("6y", adjacent("7n", 'w'))

if __name__ == '__main__':
    main()
