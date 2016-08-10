from unittest import TestCase
from unittest import main

from geotools.utils.path import Path


class GeoHashTestCase(TestCase):

    def test_hashes(self):
        london = (-0.123656, 51.51283)
        west_molesey = (-0.373535, 51.394043)
        hashes = Path([london, west_molesey]).hashes(5)
        self.assertTrue({'gcpu9', 'gcpuf', 'gcpug', 'gcpu2', 'gcpuu',  'gcpud', 'gcpu8', 'gcpsr', 'gcpvh', 'gcpvj'}.issubset(hashes))
        self.assertEqual(10, len(hashes))

if __name__ == '__main__':
    main()
