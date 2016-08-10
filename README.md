_This was originally made as a part of a location analysis prototype I was experimenting with before joining [Zenly](https://zen.ly/). I decided to pick up where I left off as a few weeks ago, I was looking for a python library that could help me to convert geojson polygon into a bunch of geohash codes._

_As I had quite a hard time finding some solid resources that work with geohashes, I thought it would be a good idea to opensource it; It is quite a simple example of how to deal and what can be made with geohashes._

![Logo](./logo.png =150x)
# Geotools 
![Status](https://img.shields.io/badge/status-stable-green.svg?style=shield) 
[![Circle CI](https://circleci.com/gh/0xC70FF3/pygeotools/tree/master.svg?style=shield)](https://circleci.com/gh/0xC70FF3/pygeotools/tree/master) 
![Coverage Status](https://img.shields.io/badge/coverage-80%-green.svg?style=shield) 
![GoDoc](http://img.shields.io/badge/licence-MIT-blue.svg?style=shield) 

This repository offers a toolbox for working with geometrical 2D shapes and geohashes.

It provides tools for exploring geohashes neighborhood as well as helpers to rasterize 2D shapes.

**Table of contents**

- [geotools](#geotools)
  - [Organization](#organization)
  - [Implementation](#implementation)
    - [Algorithms](#algorithms)
      - [Geohash Neighbourhood](#geohash-neighbourhood)    
      - [Line Segment Intersection](#line-segment-intersection)
      - [Point in Polygon Test](#point-in-polygon)
      - [Shape Rasterization](#gshape-rasterization)
    - [Further reading](#further-reading-2)
  - [Usage](#usage)
  - [License](#license-)

## Organization

```
.
├── (1) README.md
├── (2) geotools
├── (3) setup.py
├── (4) requirements.txt
└── (5) LICENSE
```

**(1)**: This [document](/README.md) (succinctly) presents our implementation and introduces various algorithms we use. It links to more detailed resources when necessary.


**(2)**: [Package `geotools`](/geotools) implements various tools for exploring geohash neighbourhood as well as helpers to rasterize shapes into a bunch of geohash quite efficiently.

**(3)**: [Module `setup.py`](/setup.py) allows you to work with PIP. You can import the whole hereby code as a PIP library by typing the folowing:
```pip install https://coveralls.io/github/0xC70FF3/geotools?branch=master```. Then just add the classic ```import``` statements to your project.

**(4)**: [File `requirements.txt`](/requirements.txt) lists all of the project dependencies and prerequisites. If using PIP, these should be installed at the same time.

**(5)**: [MIT](/LICENSE) license

## Implementation

I took a look at several alternatives in java such as geogeometry [[1]] or GeoHashesInPolygon [[2]] but the code was quite buggy and seemed to reinvent the wheel. Then, I looked directly at Apache Lucene [[3], [4]] and it seemed to do exactly what I needed but, it was so damn heavy and complicated.

I ended up recoding the few tools I needed entirely by using some efficient algorithms. This results in a clean and easy-to-use solution for covering or filling polygons with geohash bounding boxes.

I chose to rely on robust and well-used libraries like python-geohash [[5]] and geojson [[6]] wich are fast and accurate. It assumes you're using geojson, which is a format [[7]] for representing geometric shapes on the web.

### Algorithms

Below are presented the major algorithms that are used in this library.

#### Geohash neighbourhood

Finding the geohash standing north (or east, south or west) of a reference geohash is easy computing. The first alternatives I looked at were computing the center of the reference geohash bounding box, then moving it to north by adding to its latitude the height of the reference bounding box, then computing the geohash containing the resulting point. 

This seamed to be a bit too complicated since finding neightbours of a geohash is supposed to be a simple bit-wise operation.

I ended up recoding it entirely, in a recursive way by using a reference characters map. Depending on the parity of the reference geohash length, it is easy to compute the ending character of its northern neighbour (modulo 4 or 8 operation), and you eventually have to recursively compute the northern neighbour of its ```(length - 1)``` geohash parent.  

#### Line Segment Intersection [[8]]

This algorithm relies on a clever and efficient slope computation:

```python
def ccw(A,B,C):
    return (C.y-A.y)*(B.x-A.x) - (B.y-A.y)*(C.x-A.x)
```

Let say, if the slope of the line AB is less than the slope of the line AC then the three points are listed in a counterclockwise order. Then the function returns `1`.

If the slopes are equal then all three points are collinear and therefore no longer listed in a counterclockwise order the function returns `0`.

In the general case, let stay that we have two segements AB and CD. Then the two segments intersects when

```python
ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
```

All we have to do next, is handle cases where 3 points are aligned. Let say that A, B and C are aligned, then we have to check if C belongs to AB segment.

Done.

#### Point Inclusion in Polygon [[9]]

This algorithm is based on W. Randolph Franklin implementation in C. It is basically a ray-casting algorithm [[11]].

It casts a semi-infinite ray horizontally (increasing x, fixed y) out from the test point, and count how many edges it crosses. At each crossing, the ray switches between inside and outside. This is called the _Jordan curve theorem_.

The case of the ray going through a vertex is handled correctly via a careful selection of inequalities.

#### Shape Rasterization into Geohashes

The idea behind this is to transform a shape into a list of geohashes that cover the shape or that fully included into the shape (depending on the parameters).

We start by getting th ebouding box of the shape and by listing all geohashes that cover this bounding box. Then for each geohash we check if its corresponding bounding box is included or covers a part of the initial shape. We use the two previous algorithms to achieve this.

Covering a regular convex shape (like a circle) is much more easy and can be done more efficiently just by finding geohashes that covers its perimeter. Then we fill the hole.

### Performances and Efficiency

This implementation is quite fast (depending on the prevision level you provide) and I will try to improve its performances even more in future releases. For exemple I was able to get a full hierarchical rasterization of 192 country polygons up to geohash precision length 6 in less that 5 hours.


### Further reading

- [ [1] ]: https://github.com/jillesvangurp/geogeometry/ 
- [ [2] ]: https://github.com/jaredkoontz/GeoHashesInPolygon/
- [ [3] ]: http://opensourceconnections.com/blog/2014/04/11/indexing-polygons-in-lucene-with-accuracy/
- [ [4] ]: http://grepcode.com/project/repo1.maven.org/maven2/org.apache.lucene/lucene-spatial/
- [ [5] ]: https://pypi.python.org/pypi/python-geohash
- [ [6] ]: https://pypi.python.org/pypi/geojson
- [ [7] ]: http://geojson.org/geojson-spec.html
- [ [8] ]: http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
- [  [9] ]: https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
- [[10]]: https://github.com/mbostock/topojson
- [[11]]: https://en.wikipedia.org/wiki/Point_in_polygon

[1]: <https://github.com/jillesvangurp/geogeometry/> "geogeometry"
[2]: <https://github.com/jaredkoontz/GeoHashesInPolygon/> "GeoHashesInPolygon"
[3]: <http://opensourceconnections.com/blog/2014/04/11/indexing-polygons-in-lucene-with-accuracy/> "Apache Lucene"
[4]: <http://grepcode.com/project/repo1.maven.org/maven2/org.apache.lucene/lucene-spatial/> "Apache Lucene Source Code"
[5]: <https://pypi.python.org/pypi/python-geohash> "python-geohash"
[6]: <https://pypi.python.org/pypi/geojson> "python-geojson"
[7]: <http://geojson.org/geojson-spec.html> "GeoJSON format"
[8]: <http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/> "Line Segment Intersection"
[9]: <https://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html> "Point Inclusion in Polygon"
[10]:<https://github.com/mbostock/topojson> "TopoJSON"
[11]:<https://en.wikipedia.org/wiki/Point_in_polygon> "Ray casting algorithm"

## Usage
you may have a look at the [`main`](/geotools/__main__.py) file, to see basic usage of this library.

```python
print(
	Polygon([(2.395, 48.898),(2.399, 48.890), ...]).hashcodes(
				min_precision=2, 
				max_precision=7, 
				cover=False,
				adaptative=True
	)
)
```

If option `cover` is set to `True`, the algorithm tries to cover the full polygon with geohashes bounding boxes. If set to `False` it tries to fill the polygon.

The `adaptative` option allows the algorithm to use the whole range of geohash precision between `min_precision` and `max_precision`. If set to `False` you will obtain a regular grid of geohashes at `min_precision`.

## License ![License](https://img.shields.io/badge/license-MIT-blue.svg?style=shield)

The MIT License (MIT) - see LICENSE for more details

Christophe Cassagnabère <cassagnachristophe@hotmail.com> [@0xC70FF3](https://twitter.com/0xC70FF3)