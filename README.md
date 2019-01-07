svgoutline
==========

This Python library extracts all strokes (outlines) from an SVG vector graphics
file as a series of straight line segments appropriate for driving pen plotters
or desktop cutting machines.

Key features:

* **Supports most common SVG features** including beziers, shapes, text and
  dashed lines.
* **Output is just a flat list of straight lines** given as page coordinates in
  millimetres.  No transformations required.
* **Ignores out non-stroked objects.**
* **Curves are approximated by straight lines** with user-defined fidelity.
* **Captures stroke colours** in RGBA format.
* **Captures stroke widths** in millimetres.

Limitations:

* **Only [SVG Tiny 1.2](https://www.w3.org/TR/SVGTiny12/) is supported** due to the
  use of [Qt SVG](http://doc.qt.io/qt-5/qtsvg-index.html) internally. The
  following significant features are missing which you might otherwise expect:
  * Clipping masks are not supported and will be ignored.
  * Text displayed along a path is not supported and will not be rendered.
  * Adjustments to the style and position of individual parts of a text element
    are not supported (e.g. setting just one word to bold or increasing or
    decreasing the space between pairs of characters). These adjustments will
    be ignored.
* **Depends on [Qt for Python (a.k.a.
  PySide2)](https://wiki.qt.io/Qt_for_Python).**  This is a relatively
  non-trivial dependency but is easy to install from
  [PyPI](https://pypi.org/project/PySide2/) on most platforms.
* **Oblivious to fills and overlaps.** Consequently, if two shapes overlap,
  their full outlines will be included in the output regardless of what parts
  of their outlines are actually visible. For plotting purposes this should not
  be a significant problem as input SVGs are unlikely to contain filled
  elements.
* **Output does not distinguish between closed paths and paths whose start and
  end coordinates are the same.** This distinction is not important for most
  plotting applications.

Tests
-----

The tests are written using [py.test](https://docs.pytest.org/en/latest/) and
test dependencies can be installed and the tests executed with:

    $ pip install -r requirements-test.txt
    $ py.test tests

The code adheres to the Python [PEP8 style
guide](https://www.python.org/dev/peps/pep-0008/) and is checked using
[flake8](http://flake8.pycqa.org/en/latest/) (installed with py.test in the
commands above). Run it using:

    $ flake8 tests svgoutline
