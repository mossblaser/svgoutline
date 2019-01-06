import pytest

from shapely.geometry import LineString, Polygon, Point, box

from xml.etree import ElementTree

from svgoutline.svg_to_outlines import svg_to_outlines


def test_empty():
    # Simple case: An empty file
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
        </svg>
    """)
    assert svg_to_outlines(svg) == []


def test_display_none():
    # Simple case: A file with an invisible line
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:#ff0000;display:none" d="M0,0 L2,1"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == []


def test_no_stroke():
    # Simple case: A file with line not stroked
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:none" d="M0,0 L2,1"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == []


def test_straight_line():
    # Simple case: A straight red line
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:#ff0000" d="M0,0 L2,1"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        ((1, 0, 0, 1), [(0, 0), (20, 10)]),
    ]


def test_polyline():
    # Simple case: A line with several steps
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:#ffff00" d="M0,0 L0,1 L2,1 L2,0"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        ((1, 1, 0, 1), [(0, 0), (0, 10), (20, 10), (20, 0)]),
    ]


def test_rect():
    # Simple case: A <rect>
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <rect style="stroke:#ffffff" width="2" height="1" x="0" y="0"/>
        </svg>
    """)
    out = svg_to_outlines(svg)
    
    assert len(out) == 1
    colour, line = out[0]
    
    assert colour == (1, 1, 1, 1)
    
    assert len(line) == 5
    edges = set(tuple(sorted([start, end])) for start, end in zip(line, line[1:]))
    assert edges == set([
        ((0, 0), (0, 10)),
        ((0, 0), (20, 0)),
        ((20, 0), (20, 10)),
        ((0, 10), (20, 10)),
    ])


def test_dashes():
    # Simple case: A dashed path
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:black;stroke-width:1;stroke-dasharray:0.75,0.25" d="M0,0 L2,0"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        ((0, 0, 0, 1), [(0, 0), (7.5, 0)]),
        ((0, 0, 0, 1), [(10, 0), (17.5, 0)]),
    ]


def test_scale_transform():
    # Check scaling works (and also applies correctly to dashed lines)
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <g transform="scale(2, 1)">
                <path style="stroke:black;stroke-width:1;stroke-dasharray:0.75,0.25" d="M0,0 L1,0"/>
            </g>
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        ((0, 0, 0, 1), [(0, 0), (15, 0)]),
    ]


def quadratic_bezier(start, control, end, p):
    """
    Given a bezier from start (x, y) and end (x, y) with controlpoint 'control'
    (x, y), find the point at position 'p' (0.0 to 1.0) along the curve.
    """
    out = []
    for a1, a2, a3 in zip(start, control, end):
        b1 = a1 + ((a2 - a1) * p)
        b2 = a2 + ((a3 - a2) * p)
        
        out.append(b1 + ((b2 - b1) * p))
    
    return tuple(out)


def test_bezier():
    # Check bezier curves work correctly
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:black" d="M0,0 Q1,1 2,0"/>
        </svg>
    """)
    out = svg_to_outlines(svg)
    
    assert len(out) == 1
    
    colour, line = out[0]
    
    line_buf = LineString(line).buffer(0.2)
    for p in range(101):
        point = Point(quadratic_bezier((0, 0), (10, 10), (20, 0), p/100.0))
        assert line_buf.intersects(point), (p, line_buf.distance(point))


def test_text():
    # Check text is rendered sensibly
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <text style="font-size:1;stroke:black" x="0" y="1">T</text>
        </svg>
    """)
    out = svg_to_outlines(svg)
    
    assert len(out) == 1
    
    colour, line = out[0]
    
    # Since we can't really guess the font that will be used, just check for
    # sanity
    letter = Polygon(line)
    
    # Is it *approximately* the right size?
    minx, miny, maxx, maxy = letter.bounds
    width = maxx - minx
    height = maxy - miny
    assert 2 < width < 15
    assert 5 < height < 15
    
    # In approximately the right place?
    assert -2 < minx < 2
    assert -2 < miny < 5
    
    # With approximately the correct proportions (i.e. wide bit of the 'T' at
    # the top, lower parts narrower)
    btm_rect = box(minx, miny + height*0.666,
                   maxx, maxy)
    mid_rect = box(minx, miny + height*0.333,
                   maxx, miny + height*0.666)
    top_rect = box(minx, miny + height,
                   maxx, miny + height*0.333)
    btm_area = btm_rect.intersection(letter).area
    mid_area = mid_rect.intersection(letter).area
    top_area = top_rect.intersection(letter).area
    assert top_area > mid_area
    assert top_area > btm_area


@pytest.mark.parametrize("pixels_per_mm", [1.0, 2.5, 5.0, 20.0, 100.0])
def test_resolution(pixels_per_mm):
    # Check varying the resolution does correctly increase/decrease the detail
    # added to a curve
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:black" d="M0,0 Q1,1 2,0"/>
        </svg>
    """)
    out = svg_to_outlines(svg, pixels_per_mm=pixels_per_mm)
    
    assert len(out) == 1
    
    colour, line = out[0]
    
    line_buf = LineString(line).buffer(1.0 / pixels_per_mm)
    line_fine_buf = LineString(line).buffer(0.01 / pixels_per_mm)
    
    points_on_bezier = [
        Point(quadratic_bezier((0, 0), (10, 10), (20, 0), p/1000.0))
        for p in range(1001)
    ]
    
    # All points should be within the expected tollerance for this level of
    # detail.
    assert all(line_buf.intersects(point) for point in points_on_bezier)
    
    # When we use an excessively fine tollerance for the detail level tested,
    # some points may not lie on the line.
    assert not all(line_fine_buf.intersects(point) for point in points_on_bezier)


def test_use():
    # Make sure <use> directives work
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <path id="p1" style="stroke:#ff0000" d="M0,0 L2,0"/>
            <use
              x="0"
              y="0"
              href="#p1"
              width="100%"
              height="100%"
              transform="translate(0, 1)"
            />
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        ((1, 0, 0, 1), [(0, 0), (20, 0)]),
        ((1, 0, 0, 1), [(0, 10), (20, 10)]),
    ]


def test_gradient():
    # Make sure gradient strokes result in 'None' as the output colour.
    svg = ElementTree.fromstring("""
        <svg width="2cm" height="1cm" viewBox="0 0 2 1">
            <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="2" y2="1">
                    <stop style="stop-color:red" offset="0"/>
                    <stop style="stop-color:blue" offset="1"/>
                </linearGradient>
            </defs>
            <path id="p1" style="stroke:url(#g1)" d="M0,0 L2,1"/>
        </svg>
    """)
    assert svg_to_outlines(svg) == [
        (None, [(0, 0), (20, 10)]),
    ]
