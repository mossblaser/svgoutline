#!/usr/bin/env python

"""
A script provided for demonstration purposes which extracts the outlines from
an SVG and generates a new SVG illustrating the output.
"""

import sys

from xml.etree import ElementTree

from argparse import ArgumentParser

from svgoutline import get_svg_page_size, svg_to_outlines


def main():
    parser = ArgumentParser(description="""
        Extract the outlines from an SVG file, illustrating the output in a new
        SVG. Reads an SVG from stdin and writes a new SVG to stdout.
    """)

    parser.add_argument(
        "--pixels-per-mm", "-p",
        type=float, default=5,
        help="Resolution to use for converting curves to lines.")

    parser.add_argument(
        "--line-width-override", "-l",
        type=str,
        help="""
            Override the line width for all lines to this many mm or other CSS
            units.
        """)

    parser.add_argument(
        "--colour-override", "-c",
        nargs=4, type=float, metavar=("R", "G", "B", "A"),
        help="""
            Override the line colour for all lines. R, G, B, A in range 0.0 to
            1.0.
        """)

    args = parser.parse_args()

    svg = ElementTree.parse(sys.stdin).getroot()
    outlines = svg_to_outlines(
        svg, pixels_per_mm=args.pixels_per_mm)
    width_mm, height_mm = get_svg_page_size(svg)

    # Generate a new SVG as output which just contains the line segments
    # extracted from the source.
    builder = ElementTree.TreeBuilder()
    builder.start("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "version": "1.1",
        "width": "{}mm".format(width_mm),
        "height": "{}mm".format(height_mm),
        "viewBox": "0 0 {} {}".format(width_mm, height_mm)
    })

    # Define markers for line starts and vertices
    mm_per_pixel = 25.4 / 96.0
    builder.start("defs")
    builder.start("rect", {
        "id": "start",
        "style": "fill:white;stroke:black;stroke-width:{}".format(
            mm_per_pixel),
        "x": str(-mm_per_pixel*2),
        "y": str(-mm_per_pixel*2),
        "width": str(mm_per_pixel*5),
        "height": str(mm_per_pixel*5),
    })
    builder.end("rect")
    builder.start("use", {
        "id": "end",
        "xlink:href": "#start",
    })
    builder.end("use")
    builder.start("circle", {
        "id": "vertex",
        "style": "fill:black;stroke:none",
        "r": str(mm_per_pixel*2),
    })
    builder.end("circle")
    builder.end("defs")

    # Draw the lines
    for colour, width, points in outlines:
        if args.line_width_override is not None:
            width = args.line_width_override
        if args.colour_override is not None:
            colour = args.colour_override

        # Draw line
        x, y = points[0]
        r, g, b, a = colour or (0, 0, 0, 1)
        builder.start("path", {
            "d": "M{},{} {}".format(
                x, y,
                " ".join("L{},{}".format(x, y) for x, y in points[1:]),
            ),
            "style": """
                fill:none;
                stroke:#{:02x}{:02x}{:02x};
                stroke-opacity:{};
                stroke-width:{}
            """.format(int(255*r), int(255*g), int(255*b), a,
                       width),
        })
        builder.end("path")

        # Draw vertex markers
        for x, y in points[1:-1]:
            builder.start("use", {
                "xlink:href": "#vertex",
                "transform": "translate({}, {})".format(x, y)
            })
            builder.end("use")

        # Draw start/end markers
        if points[0] != points[-1]:
            x, y = points[0]
            builder.start("use", {
                "xlink:href": "#start",
                "transform": "translate({}, {})".format(x, y)
            })
            builder.end("use")

            x, y = points[-1]
            builder.start("use", {
                "xlink:href": "#end",
                "transform": "translate({}, {})".format(x, y),
            })
            builder.end("use")
        else:
            x, y = points[0]
            builder.start("use", {
                "xlink:href": "#vertex",
                "transform": "translate({}, {})".format(x, y)
            })
            builder.end("use")

    builder.end("svg")

    print(ElementTree.tostring(builder.close(), "unicode"))


if __name__ == "__main__":
    main()
