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


class Circle:

    def __init__(self, point, radius):
        self.center = point
        self.radius = radius
        validate(point[0], point[1])
        # basically the algorithm can go into an endless loop. Best to avoid the poles.
        if point[1] < -89.75 or point[1] > 89.75:
            raise ValueError("please stay away from the north pole or the south pole; there are some known issues there. Besides, nothing there but snow and ice.")
        self.__bbox = {
            "n": destination_point(self.center, self.radius, 0)[1],
            "s": destination_point(self.center, self.radius, 180)[1],
            "e": destination_point(self.center, self.radius, 270)[0],
            "w": destination_point(self.center, self.radius, 90)[0]
        }

    def bbox(self):
        return self.__bbox

    def __is_included(self, bbox):
        sw = (bbox["w"], bbox["s"])
        se = (bbox["e"], bbox["s"])
        nw = (bbox["w"], bbox["n"])
        ne = (bbox["e"], bbox["n"])

        if bbox["w"] < self.center[0] < bbox["e"]:
            return distance(self.center, (self.center[0], bbox['n'])) <= self.radius or distance(self.center, (self.center[0], bbox['s'])) <= self.radius
        if bbox["s"] < self.center[1] < bbox["n"]:
            return distance(self.center, (bbox['w'], self.center[1])) <= self.radius or distance(self.center, (bbox['e'], self.center[1])) <= self.radius

        return distance(self.center, sw) <= self.radius \
               or distance(self.center, se) <= self.radius \
               or distance(self.center, nw) <= self.radius \
               or distance(self.center, ne) <= self.radius

    @staticmethod
    def __recenter(lon):
        return lon if -180 < lon < 180 else lon + 360 if -180 > lon else lon - 360

    def hashcodes(self, hashlength=10):
        west_set, east_set, hashcodes = set(), set(), set()

        row_hashcode = geohash.encode(latitude=self.__bbox["s"], longitude=self.__bbox["w"], precision=hashlength)
        row_bbox = geohash.bbox(row_hashcode)
        while row_bbox["s"] < self.__bbox["n"]:
            cell_hashcode = row_hashcode
            cell_bbox = row_bbox
            while is_west(cell_bbox["w"], self.__bbox["e"]):
                if self.__is_included(cell_bbox):
                    west_set.add(cell_hashcode)
                    break
                cell_hashcode = east(cell_hashcode)
                cell_bbox = geohash.bbox(cell_hashcode)
            row_hashcode = north(row_hashcode)
            row_bbox = geohash.bbox(row_hashcode)

        row_hashcode = geohash.encode(latitude=self.__bbox["s"], longitude=self.__bbox["e"], precision=hashlength)
        row_bbox = geohash.bbox(row_hashcode)
        while row_bbox["s"] < self.__bbox["n"]:
            cell_hashcode = row_hashcode
            cell_bbox = row_bbox
            while not is_west(cell_bbox["e"], self.__bbox["w"]):
                if self.__is_included(cell_bbox):
                    east_set.add(cell_hashcode)
                    break
                cell_hashcode = west(cell_hashcode)
                cell_bbox = geohash.bbox(cell_hashcode)
            row_hashcode = north(row_hashcode)
            row_bbox = geohash.bbox(row_hashcode)

        for hashcode in west_set:
            current = hashcode
            while current not in east_set:
                hashcodes.add(current)
                current = east(current)
        hashcodes.update(west_set)
        hashcodes.update(east_set)
        return hashcodes
