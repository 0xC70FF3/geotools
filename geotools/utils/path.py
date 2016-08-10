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


class Path:

    def __init__(self, path):
        if not path or len(path) < 2:
            raise ValueError("must have at least two way points on the path")
        self._path = path

    def hashes(self, precision=DEFAULT_PRECISION):
        """return set of geo hashes along the path with the specified geo hash length
        """
        return Path._hashes(self._path, precision)

    @staticmethod
    def _hashes(path, precision=DEFAULT_PRECISION):
        if len(path) == 2:
            line = path
            curr_hash = geohash.encode(longitude=line[0][0], latitude=line[0][1], precision=precision)
            dest_hash = geohash.encode(longitude=line[1][0], latitude=line[1][1], precision=precision)
            hashes = {dest_hash: None}
            n, e, w, s = True, True, True, True
            while curr_hash != dest_hash:
                hashes[curr_hash] = None
                bbox0 = geohash.bbox(curr_hash)
                line0 = ((bbox0["w"], bbox0["s"]), (bbox0["e"], bbox0["s"]))
                line1 = ((bbox0["e"], bbox0["s"]), (bbox0["e"], bbox0["n"]))
                line2 = ((bbox0["e"], bbox0["n"]), (bbox0["w"], bbox0["n"]))
                if s and intersects(line, line0):
                    curr_hash, n = south(curr_hash), False
                elif e and intersects(line, line1):
                    curr_hash, w = east(curr_hash), False
                elif n and intersects(line, line2):
                    curr_hash, s = north(curr_hash), False
                else:
                    curr_hash, e = west(curr_hash), False
        else:
            hashes = dict((key, None) for key in Path.hashes(path[0:2], precision))
            hashes.update(dict((key, None) for key in Path.hashes(path[1:], precision)))

        return list(hashes.keys())

