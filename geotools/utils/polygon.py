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
from geotools.utils import *
import geohash


class Polygon:

    def __init__(self, coordinates):
        """return bounding box that contains the polygon as an array of [minLon, minLat, maxLon, maxLat]
        """
        if len(coordinates) < 3:
            raise ValueError("a polygon must have at least three points")
        self._coordinates = coordinates
        self._bbox = dict()
        for lon, lat in coordinates:
            validate(lon, lat)
            # basically the algorithm can go into an endless loop. Best to avoid the poles.
            if lat < -89.75 or lat > 89.75:
                raise ValueError("please stay away from the north pole or the south pole; there are some known issues there. Besides, nothing there but snow and ice.")
            self._bbox = {
                "w": lon if "w" not in self._bbox else min(lon, self._bbox["w"]),
                "s": lat if "s" not in self._bbox else min(lat, self._bbox["s"]),
                "e": lon if "e" not in self._bbox else max(lon, self._bbox["e"]),
                "n": lat if "n" not in self._bbox else max(lat, self._bbox["n"])
            }

    def bbox(self):
        return self._bbox

    # https://github.com/mapbox/leaflet-pip/blob/gh-pages/leaflet-pip.js
    def contains(self, point):
        """ray-casting algorithm based on:
                http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
        """
        inside = False
        prev = self._coordinates[-1]
        for curr in self._coordinates:
            if ((curr[1] > point[1]) != (prev[1] > point[1])) \
                    and (point[0] < (prev[0] - curr[0]) * (point[1] - curr[1]) / (prev[1] - curr[1]) + curr[0]):
                inside = not inside
            prev = curr
        return inside

    def intersects(self, bbox):
        prev = self._coordinates[-1]
        for curr in self._coordinates:  # Walk the edges of the polygon
            if intersects(((bbox["w"], bbox["s"]), (bbox["e"], bbox["s"])), (prev, curr)):
                return True
            if intersects(((bbox["e"], bbox["s"]), (bbox["e"], bbox["n"])), (prev, curr)):
                return True
            if intersects(((bbox["e"], bbox["n"]), (bbox["w"], bbox["n"])), (prev, curr)):
                return True
            if intersects(((bbox["w"], bbox["n"]), (bbox["w"], bbox["s"])), (prev, curr)):
                return True
            prev = curr
        return False

    def qcover(self, min_precision=2, max_precision=DEFAULT_PRECISION):
        return self.hashcodes(min_precision, max_precision, cover=True, quick=True)

    def cover(self, min_precision=2, max_precision=DEFAULT_PRECISION):
        return self.hashcodes(min_precision, max_precision, cover=True)

    def qfill(self, min_precision=2, max_precision=DEFAULT_PRECISION):
        return self.hashcodes(min_precision, max_precision, quick=True)

    def fill(self, min_precision=2, max_precision=DEFAULT_PRECISION):
        return self.hashcodes(min_precision, max_precision)

    def hashcodes(self, min_precision=2, max_precision=DEFAULT_PRECISION, cover=False, quick=False):
        """fills or covers the polygon with geo hashes.
        In fill mode, if a geohash partially falls outside the polygon, it is omitted.

        The algorithm works for both convex and concave algorithms.

        We're not aiming for perfect detail here in terms of 'pixellation', going beyond 9 doesn't serve much purpose.
        2 chars zone area almost covers france. It is a good start for Russia, China, US...
        """
        max_precision = min(max_precision, DEFAULT_PRECISION)
        polygon_bbox = self.bbox()

        # generate all hashes covering the containing bounding box. Starting at south west
        partially_contained = list()
        row_hashcode = geohash.encode(polygon_bbox["s"], polygon_bbox["w"], min_precision)  # beware: lat, lon
        row_bbox = geohash.bbox(row_hashcode)
        while row_bbox["s"] < polygon_bbox["n"]:
            col_hashcode = row_hashcode
            col_bbox = row_bbox
            while is_west(col_bbox["w"], polygon_bbox["e"]):
                partially_contained.append(col_hashcode)
                col_hashcode = east(col_hashcode)
                col_bbox = geohash.bbox(col_hashcode)
            # move to the next row
            row_hashcode = north(row_hashcode)
            row_bbox = geohash.bbox(row_hashcode)

        # filter hashes and decompose while max_precision is not reached
        fully_contained = list()
        curr_precision = min_precision
        while curr_precision <= max_precision:
            other_fully_contained, partially_contained = \
                self._quick_filter(partially_contained, curr_precision < max_precision, cover=cover) if quick \
                else self._filter(partially_contained, curr_precision < max_precision, cover=cover)
            fully_contained.extend(other_fully_contained)
            curr_precision += 1

        # if len(fully_contained) == 0:  # if no inner bbox found and can't go further, then cover?
        #     fully_contained.extend(partially_contained)
        return fully_contained

    def _quick_filter(self, hashcodes, split=True, cover=False):
        """this way of filtering induces a small bias since we consider only corners of bboxes.
        However it is much quicker.
        """
        fully_contained = list()
        partially_contained = list()
        for hashcode in hashcodes:
            bbox = geohash.bbox(hashcode)
            _oddity = self.contains((bbox['e'], bbox['s']))
            if _oddity and not split and cover:
                fully_contained.append(hashcode)
            elif _oddity != self.contains((bbox['w'], bbox['s'])):
                if split:  # decompose into smaller pieces
                    partially_contained.extend(subhashcodes(hashcode))
                elif cover:
                    fully_contained.append(hashcode)
                # else out
            elif _oddity != self.contains((bbox['w'], bbox['n'])):
                if split:  # decompose into smaller pieces
                    partially_contained.extend(subhashcodes(hashcode))
                elif cover:
                    fully_contained.append(hashcode)
                # else out
            elif _oddity != self.contains((bbox['e'], bbox['n'])):
                if split:  # decompose into smaller pieces
                    partially_contained.extend(subhashcodes(hashcode))
                elif cover:
                    fully_contained.append(hashcode)
                # else out
            elif _oddity:
                fully_contained.append(hashcode)
            # else out
        return fully_contained, partially_contained

    def _filter(self, hashcodes, split=True, cover=False):
        fully_contained = list()
        partially_contained = list()
        for hashcode in hashcodes:
            bbox = geohash.bbox(hashcode)
            if self.intersects(bbox) or\
                    matches(*self._coordinates[0], hashcode):  # bbox contains polygon:
                if split:
                    partially_contained.extend(subhashcodes(hashcode))  # decompose into smaller pieces
                elif cover:
                    fully_contained.append(hashcode)
                # else out
            else:
                if self.contains((bbox['e'], bbox['s'])) and \
                        self.contains((bbox['w'], bbox['s'])) and \
                        self.contains((bbox['w'], bbox['n'])) and \
                        self.contains((bbox['e'], bbox['n'])):  # if whole bbox is inside
                    fully_contained.append(hashcode)
                # else out

        return fully_contained, partially_contained
