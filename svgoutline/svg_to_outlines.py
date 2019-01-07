from xml.etree import ElementTree

from PySide2.QtGui import QGuiApplication
from PySide2.QtGui import QPainter
from PySide2.QtSvg import QSvgRenderer
from PySide2.QtCore import QXmlStreamReader

from svgoutline.svg_utils import namespaces, get_svg_page_size
from svgoutline.outline_painter import OutlinePaintDevice


# Tell ElementTree to use the conventional namespace aliases for the basic
# namespaces used by SVG. This is not strictly necessary for generating valid
# SVG files but some incorrectly written clients may misbehave (notably Qt's
# QSvg) if these names are not used.
try:
    register_xml_namespace = ElementTree.register_namespace
except AttributeError:
    def register_xml_namespace(prefix, uri):
        ElementTree._namespace_map[uri] = prefix
for prefix, uri in namespaces.items():
    register_xml_namespace(prefix, uri)


def svg_to_outlines(root, width_mm=None, height_mm=None, pixels_per_mm=5.0):
    """
    Given an SVG as a Python ElementTree, return a set of straight line
    segments which approximate the outlines in that SVG when rendered.

    Occlusion is not accounted for in the returned list of outlines. Even if
    one shape is completely occluded by another, both of their outlines will be
    reported. Simillarly, overlapping lines will also be passed through.

    .. note::

        This function internally uses the QSvg library from Qt to render the
        provided SVG to a special painting backend which captures the output
        lines. As a consequence, SVG feature support is as good or as bad as
        that library. QSvg is generally regarded as a high quality and
        relatively complete SVG implementation and so most SVG features should
        be supported.

    .. note::

        Due to its internal use of Qt, a PySide2.QtGui.QGuiApplication will be
        created if one has not already been created. Non-Qt users and most Qt
        users should not be affected by this.

    Parameters
    ----------
    root : ElementTree
        The SVG whose outlines should be extracted.
    width_mm, height_mm : float or None
        The page size to render the SVG at (in milimeters). If omitted, this
        will be determined automatically from the SVG's width and height
        attributes. These arguments are mandatory for SVGs lacking these
        attributes.
    pixels_per_mm : float
        Curved outlines will be approximated by straight lines in the output.
        This parameter controls how exactly curves will be approximated.
        Specifically, the curve approximation will be at least fine enough for
        rasterised versions of the lines to 'look right' at the specified pixel
        density.

    Returns
    -------
    [((r, g, b, a) or None, width, [(x, y), ...]), ...]
        A list of polylines described by (colour, line) pairs.

        The 'colour' values define the colour used to draw the line (if a solid
        colour was used) or None (if a gradient or patterned stroke was used).
        Colours are given as four-tuples in RGBA order with values from 0.0 to
        1.0.

        The 'width' value gives the line width used to draw the line (given in
        mm). If the shape being drawn has a non-uniform scaling applied, this
        value may not be meaningful and its actual value should be considered
        undefined.

        The 'line' part of each tuple defines the outline as a series of (x, y)
        coordinates (given in mm) which describe a continuous polyline. These
        polylines may be considered open. Closed lines in the input SVG will
        result in polylines where the first and last coordinate are identical.
        Lines may go beyond the bounds of the designated page size (as in the
        input SVG).
    """
    # This method internally uses various parts of Qt which require that a Qt
    # application exists. If one does not exist, one will be created.
    if QGuiApplication.instance() is None:
        QGuiApplication()

    # Determine the page size from the document if necessary
    if width_mm is None or height_mm is None:
        width_mm, height_mm = get_svg_page_size(root)

    # Load the SVG into QSvg
    xml_stream_reader = QXmlStreamReader()
    xml_stream_reader.addData(ElementTree.tostring(root, "unicode"))
    svg_renderer = QSvgRenderer()
    svg_renderer.load(xml_stream_reader)

    # Paint the SVG into the OutlinePaintDevice which will capture the set of
    # line segments which make up the SVG as rendered.
    outline_paint_device = OutlinePaintDevice(
        width_mm, height_mm, pixels_per_mm)
    painter = QPainter(outline_paint_device)
    try:
        svg_renderer.render(painter)
    finally:
        painter.end()

    return outline_paint_device.getOutlines()
