import pytest

from shapely.geometry import LineString, Polygon, Point, box

from xml.etree import ElementTree

from svgoutline.svg_to_outlines import svg_to_outlines


def test_empty():
    # Simple case: An empty file
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
        </svg>
    """
    )
    assert svg_to_outlines(svg) == []


def test_display_none():
    # Simple case: A file with an invisible line
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path
              style="stroke-width:0.1;stroke:#ff0000;display:none"
              d="M0,0 L2,1"
            />
        </svg>
    """
    )
    assert svg_to_outlines(svg) == []


def test_no_stroke():
    # Simple case: A file with line not stroked
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke:none" d="M0,0 L2,1"/>
        </svg>
    """
    )
    assert svg_to_outlines(svg) == []


@pytest.mark.parametrize(
    "element",
    [
        """
            <line
                style="stroke-width:0.1;stroke:#ff0000"
                x1="0"
                y1="0"
                x2="2"
                y2="1"
            />
        """,
        """
            <path style="stroke-width:0.1;stroke:#ff0000" d="M0,0 L2,1"/>
        """,
    ],
)
def test_straight_line(element: str):
    # Simple case: A straight red line
    svg = ElementTree.fromstring(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            {element}
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        ((1, 0, 0, 1), 1, [(0, 0), (20, 10)]),
    ]


@pytest.mark.parametrize(
    "element",
    [
        """
            <polyline
              style="stroke-width:0.1;stroke:#ffff00"
              points="0 0 0 1 2 1 2 0"
            />
        """,
        """
            <!-- Non-standard but common syntax -->
            <polyline
              style="stroke-width:0.1;stroke:#ffff00"
              points="0,0 0 ,1 2, 1 2 , 0"
            />
        """,
        """
            <path
              style="stroke-width:0.1;stroke:#ffff00"
              d="M0,0 L0,1 L2,1 L2,0"
            />
        """,
    ],
)
def test_polyline(element: str):
    # Simple case: A line with several steps
    svg = ElementTree.fromstring(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            {element}
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        ((1, 1, 0, 1), 1, [(0, 0), (0, 10), (20, 10), (20, 0)]),
    ]


@pytest.mark.parametrize(
    "element",
    [
        """
            <polygon
              style="stroke-width:0.1;stroke:#ffff00"
              points="0 0 0 1 2 1 2 0"
            />
        """,
        """
            <!-- Non-standard but common syntax -->
            <polygon
              style="stroke-width:0.1;stroke:#ffff00"
              points="0,0 0 ,1 2, 1 2 , 0"
            />
        """,
        """
            <path
              style="stroke-width:0.1;stroke:#ffff00"
              d="M0,0 L0,1 L2,1 L2,0 Z"
            />
        """,
    ],
)
def test_polygon(element: str):
    # Simple case: A line with several steps
    svg = ElementTree.fromstring(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            {element}
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        ((1, 1, 0, 1), 1, [(0, 0), (0, 10), (20, 10), (20, 0), (0, 0)]),
    ]


def test_rect():
    # Simple case: A <rect>
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <rect
              style="stroke-width:0.1;stroke:#ffffff"
              width="2"
              height="1"
              x="0"
              y="0"
            />
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    assert len(out) == 1
    colour, width, line = out[0]

    assert colour == (1, 1, 1, 1)
    assert width == 1

    assert len(line) == 5
    edges = set(tuple(sorted([start, end])) for start, end in zip(line, line[1:]))
    assert edges == set(
        [
            ((0, 0), (0, 10)),
            ((0, 0), (20, 0)),
            ((20, 0), (20, 10)),
            ((0, 10), (20, 10)),
        ]
    )


def test_dashes():
    # Simple case: A dashed path
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path
              style="stroke-width:1;stroke:black;stroke-width:1;stroke-dasharray:0.75,0.25"
              d="M0,0 L2,0"
            />
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        ((0, 0, 0, 1), 10, [(0, 0), (7.5, 0)]),
        ((0, 0, 0, 1), 10, [(10, 0), (17.5, 0)]),
    ]


def test_scale_transform():
    # Check scaling works (and also applies correctly to dashed lines)
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <g transform="scale(2, 1)">
                <path
                  style="stroke:black;stroke-width:1;stroke-dasharray:0.75,0.25"
                  d="M0,0 L1,0"
                />
            </g>
        </svg>
    """
    )
    out = svg_to_outlines(svg)
    assert len(out) == 1
    colour, width, lines = out[0]
    assert colour == (0, 0, 0, 1)
    assert lines == [(0, 0), (15, 0)]


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
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke-width:0.1;stroke:black" d="M0,0 Q1,1 2,0"/>
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    assert len(out) == 1

    colour, width, line = out[0]

    line_buf = LineString(line).buffer(0.2)
    for p in range(101):
        point = Point(quadratic_bezier((0, 0), (10, 10), (20, 0), p / 100.0))
        assert line_buf.intersects(point), (p, line_buf.distance(point))


def test_text():
    # Check text is rendered sensibly
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <text
              style="stroke-width:0.1;font-size:1;stroke:black"
              x="0" y="1"
            >T</text>
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    assert len(out) == 1

    colour, width, line = out[0]

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
    btm_rect = box(minx, miny + height * 0.666, maxx, maxy)
    mid_rect = box(minx, miny + height * 0.333, maxx, miny + height * 0.666)
    top_rect = box(minx, miny + height, maxx, miny + height * 0.333)
    btm_area = btm_rect.intersection(letter).area
    mid_area = mid_rect.intersection(letter).area
    top_area = top_rect.intersection(letter).area
    assert top_area > mid_area
    assert top_area > btm_area


@pytest.mark.xfail(strict=True, reason="QtSVG Bug QTBUG-72997")
def test_text_line_width_and_colour():
    # Check text is rendered with the correct line width and colour
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <text
              style="stroke-width:0.1;font-size:1;stroke:black"
              x="0" y="1"
            >T</text>
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    assert len(out) == 1

    colour, width, line = out[0]

    assert colour == (0, 0, 0, 1)
    assert width == 1


@pytest.mark.parametrize("pixels_per_mm", [1.0, 2.5, 5.0, 20.0, 100.0])
def test_resolution(pixels_per_mm):
    # Check varying the resolution does correctly increase/decrease the detail
    # added to a curve
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path style="stroke-width:0.1;stroke:black" d="M0,0 Q1,1 2,0"/>
        </svg>
    """
    )
    out = svg_to_outlines(svg, pixels_per_mm=pixels_per_mm)

    assert len(out) == 1

    colour, width, line = out[0]

    line_buf = LineString(line).buffer(1.0 / pixels_per_mm)
    line_fine_buf = LineString(line).buffer(0.01 / pixels_per_mm)

    points_on_bezier = [
        Point(quadratic_bezier((0, 0), (10, 10), (20, 0), p / 1000.0))
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
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <path
              id="p1"
              style="stroke-width:0.1;stroke:#ff0000" d="M0,0 L2,0"
            />
            <use
              x="0"
              y="0"
              href="#p1"
              width="100%"
              height="100%"
              transform="translate(0, 1)"
            />
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        ((1, 0, 0, 1), 1, [(0, 0), (20, 0)]),
        ((1, 0, 0, 1), 1, [(0, 10), (20, 10)]),
    ]


def test_gradient():
    # Make sure gradient strokes result in 'None' as the output colour.
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="2" y2="1">
                    <stop style="stop-color:red" offset="0"/>
                    <stop style="stop-color:blue" offset="1"/>
                </linearGradient>
            </defs>
            <path
              id="p1"
              style="stroke-width:0.1;stroke:url(#g1)"
              d="M0,0 L2,1"
            />
        </svg>
    """
    )
    assert svg_to_outlines(svg) == [
        (None, 1, [(0, 0), (20, 10)]),
    ]


def test_text_paths():
    # Test for text-on-path support. This is not provided in SVG Tiny 1.2 and
    # so is not expected to work here so this test actually checks for
    # non-functioning text path support to spot if this changes in the future.
    #
    # When text path support works correctly, a 'T' will be rendered upside
    # down since the path it is on runs from right-to-left.
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1"
          xmlns:xlink="http://www.w3.org/1999/xlink">
          <path
             id="p0"
             d="M2,0 L0,0"
           />
          <text
             style="font-size:1;stroke-width:0.1"
             id="text38403">
            <textPath
               xlink:href="#p0"
               id="textPath38413">T</textPath>
          </text>
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    # Currently unsupported so expect no text to be shown.
    assert len(out) == 0


def test_text_spans():
    # <tspan> is not supported in SVG Tiny 1.2 and these tags should be ignored
    # (though their contents retained, just in the wrong space). This test just
    # checks this is occurring and that support has not been added without
    # being noticed...
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <text
              style="stroke-width:0.1;font-size:1;stroke:black"
              x="0" y="1"
            >T<tspan dy="1">T</tspan></text>
        </svg>
    """
    )
    out = svg_to_outlines(svg)

    assert len(out) == 2

    colour_0, width_0, line_0 = out[0]
    colour_1, width_1, line_1 = out[1]

    letter_0 = Polygon(line_0)
    letter_1 = Polygon(line_1)

    letter_0_ymin = letter_0.bounds[1]
    letter_1_ymin = letter_1.bounds[1]

    assert letter_0_ymin == letter_1_ymin


def test_occlusion():
    # Occlusion is not supported; this test make sure this doesn't change
    # without me noticing...
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <rect
              style="fill:white;stroke-width:0.1;stroke:#00ff00"
              width="2"
              height="1"
              x="0"
              y="0"
            />
            <rect
              style="fill:white;stroke-width:0.1;stroke:#ff0000"
              width="1"
              height="1"
              x="1"
              y="0"
            />
        </svg>
    """
    )
    (
        (colour_0, width_0, lines_0),
        (colour_1, width_1, lines_1),
    ) = svg_to_outlines(svg)

    assert colour_0 == (0, 1, 0, 1)
    assert colour_1 == (1, 0, 0, 1)

    assert width_0 == width_1 == 1

    assert Polygon(lines_0).equals(box(0, 0, 20, 10))
    assert Polygon(lines_1).equals(box(10, 0, 20, 10))


def test_clipping():
    # Clipping is not part of the SVG Tiny 1.2 spec and clipping paths will be
    # ignored. This test checks that this doesn't change unepxectedly.
    svg = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg" width="2cm" height="1cm" viewBox="0 0 2 1">
            <defs>
                <clipPath id="clip0" clipPathUnits="userSpaceOnUse">
                    <rect
                      style="fill:white"
                      width="1"
                      height="1"
                      x="-0.5"
                      y="-0.5"
                    />
                </clipPath>
            </defs>
            <rect
              clip-path="url(#clip0)"
              style="stroke-width:0.1;stroke:#00ff00"
              width="2"
              height="1"
              x="0"
              y="0"
            />
        </svg>
    """
    )
    ((colour, width, lines),) = svg_to_outlines(svg)

    assert colour == (0, 1, 0, 1)
    assert width == 1

    # Expect no clipping to actually take place
    assert Polygon(lines).equals(box(0, 0, 20, 10))

    # For reference: Assertion if clipping paths worked:
    # assert Polygon(lines).equals(LineString([(0, 5), (0, 0), (5, 0)])), lines


def test_rgb_values():
    lines = ""
    for i in range(256):
        lines += f"""
            <line
                style="stroke-width:0.1;stroke:rgb({i},0,0)"
                x1="0" x2="1"
                y1="{i}" y2="{i}"
            />
            <line
                style="stroke-width:0.1;stroke:rgb(0,{i},0)"
                x1="1" x2="2"
                y1="{i}" y2="{i}"
            />
            <line
                style="stroke-width:0.1;stroke:rgb(0,0,{i})"
                x1="2" x2="3"
                y1="{i}" y2="{i}"
            />
        """

    lines = svg_to_outlines(
        ElementTree.fromstring(
            f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="30cm" height="30cm" viewBox="0 0 300 300">
                    {lines}
                </svg>
            """
        )
    )
    assert len(lines) == 256 * 3
    coord_to_colour = {(points[0][0], points[0][1]): rgba for rgba, _, points in lines}
    for i in range(256):
        assert coord_to_colour[(0, i)] == (i / 255, 0, 0, 1.0)
        assert coord_to_colour[(1, i)] == (0, i / 255, 0, 1.0)
        assert coord_to_colour[(2, i)] == (0, 0, i / 255, 1.0)


def test_alpha_values():
    lines = ""
    for i in range(256):
        lines += f"""
            <line
                style="stroke-width:0.1;stroke:black"
                opacity="{i/255}"
                x1="0" x2="1"
                y1="{i}" y2="{i}"
            />
        """
    lines = svg_to_outlines(
        ElementTree.fromstring(
            f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="30cm" height="30cm" viewBox="0 0 300 300">
                    {lines}
                </svg>
            """
        )
    )
    assert len(lines) == 256
    coord_to_colour = {(points[0][0], points[0][1]): rgba for rgba, _, points in lines}
    for i in range(256):
        assert coord_to_colour[(0, i)] == (0, 0, 0, i / 255)
