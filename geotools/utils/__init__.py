#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The MIT License (MIT)

Copyright (c) 2016 Christophe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import geohash
from geopy.distance import GreatCircleDistance


DEFAULT_PRECISION = 9
# # note: no a,i,l, and o
BASE = '0123456789bcdefghjkmnpqrstuvwxyz'
NEIGHBOURS = {
    'n': ['p0r21436x8zb9dcf5h7kjnmqesgutwvy', 'bc01fg45238967deuvhjyznpkmstqrwx'],
    's': ['14365h7k9dcfesgujnmqp0r2twvyx8zb', '238967debc01fg45kmstqrwxuvhjyznp'],
    'e': ['bc01fg45238967deuvhjyznpkmstqrwx', 'p0r21436x8zb9dcf5h7kjnmqesgutwvy'],
    'w': ['238967debc01fg45kmstqrwxuvhjyznp', '14365h7k9dcfesgujnmqp0r2twvyx8zb']
}
EDGE_CASES = {
    'n': ['prxz', 'bcfguvyz'],
    's': ['028b', '0145hjnp'],
    'e': ['bcfguvyz', 'prxz'],
    'w': ['0145hjnp', '028b']
}


def is_west(lon0, lon1):
    clon0, clon1 = lon0 + 180, lon1 + 180
    return (clon0 < clon1 and clon1 - clon0 < 180) or (clon0 > clon1 and clon1 + 360 - clon0 < 180)


def north(hashcode):
    return adjacent(hashcode, 'n')


def south(hashcode):
    return adjacent(hashcode, 's')


def east(hashcode):
    return adjacent(hashcode, 'e')


def west(hashcode):
    return adjacent(hashcode, 'w')


def adjacent(hashcode, direction):
    # based on https://github.com/davetroy/geohash-js
    # https://github.com/chrisveness/latlon-geohash/blob/master/latlon-geohash.js
    if not hashcode:
        raise ValueError('Invalid geohash')
    if direction not in 'nsew':
        raise ValueError('Invalid direction')

    r, c = hashcode[:-1], hashcode[-1]
    odd = len(hashcode) % 2
    # check for edge-cases which don't share common prefix
    if c in EDGE_CASES[direction][odd]:
        r = adjacent(r, direction) if r else None if direction in 'ns' else ''

    # append letter for direction to parent
    return r + BASE[NEIGHBOURS[direction][odd].index(c)] if r is not None else None


def validate(longitude, latitude, strict=False):
    rounded_lat = latitude
    rounded_lon = longitude
    if not strict:
        # this gets rid of rounding errors e.g. 180.00000023 will validate
        rounded_lon = round(longitude, 6)
        rounded_lat = round(latitude, 6)

    if rounded_lon < -180.0 or rounded_lon > 180.0:
        raise ValueError("Longitude {0:f} is outside legal range of -180,180".format(longitude))
    if rounded_lat < -90.0 or rounded_lat > 90.0:
        raise ValueError("Latitude {0:f} is outside legal range of -90,90".format(latitude))

    return True

def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def _within(p, q, r):
    return p[0] < q[0] < r[0] or r[0] < q[0] < p[0] or p[1] < q[1] < r[1] or r[1] < q[1] < p[1]


def intersects(line1, line2):
    sl1 = _ccw(line1[0], line2[0], line2[1])
    if not sl1 and _within(line2[0], line1[0], line2[1]):
        return True
    sl2 = _ccw(line1[1], line2[0], line2[1])
    if not sl2 and _within(line2[0], line1[1], line2[1]):
        return True
    sl3 = _ccw(line1[0], line1[1], line2[0])
    if not sl3 and _within(line1[0], line2[0], line1[1]):
        return True
    sl4 = _ccw(line1[0], line1[1], line2[1])
    if not sl4 and _within(line1[0], line2[1], line1[1]):
        return True
    return (sl1 > 0) != (sl2 > 0) and (sl3 > 0) != (sl4 > 0)


def subhashcodes(hashcode):
    """return the 32 geo hashes this geohash can be divided into."""
    return [hashcode + c for c in BASE]


def matches(lon, lat, hashcode):
    return hashcode == geohash.encode(longitude=lon, latitude=lat, precision=len(hashcode))


# TODO passer tous les parametres en lat, lon
def distance(point0, point1):
    return GreatCircleDistance((point0[1], point0[0]), (point1[1], point1[0])).meters


def destination_point(point, distance, bearing):
    p = GreatCircleDistance(meters=distance).destination((point[1], point[0]), bearing=bearing)
    return p.longitude, p.latitude
