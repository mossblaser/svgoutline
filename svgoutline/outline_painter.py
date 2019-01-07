"""
A QPaintDevice which, when painted with vector input, collects the line
segments drawn.

Qt's QPainter infrastructure makes it really easy to implement new back-ends
and Qt even provides default method implementations which handle the most
complex drawing commands (e.g. Beziers, Text etc.) converting these into
straight line segments.

The backend implemented in this module may be used along with QSvg to turn SVG
documents into lists of line segments ready for cutting/drawing with a plotter.
"""

import warnings
import math

from itertools import cycle
try:
    from itertools import izip
except ImportError:
    izip = zip

from PySide2.QtGui import QPainter
from PySide2.QtGui import QPaintDevice
from PySide2.QtGui import QPaintEngine

from PySide2.QtCore import Qt
from PySide2.QtCore import QLineF

from PySide2.QtGui import QPen
from PySide2.QtGui import QTransform


def split_line(line, offset):
    """
    Given a line defined by [(x, y), ...], split the line into two lines: the
    part of the line before 'offset' distance along the line and the part of
    the line afterwards.
    """
    # Split point before start
    if offset <= 0:
        return [], line

    for i, ((x1, y1), (x2, y2)) in enumerate(zip(line, line[1:])):
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt((dx*dx) + (dy*dy))

        if length < offset:
            # Split point comes later
            offset -= length
        elif length == offset:
            # Split point exactly on (x2, y2)
            before = line[:i+2]
            after = line[i+1:]

            # Special case: don't leave just the final point in the after list
            # since that isn't really useful...
            if len(after) == 1:
                after = []

            return before, after
        else:
            # Split point between (x1, y1) and (x2, y2)
            xm = x1 + (dx * (offset / length))
            ym = y1 + (dy * (offset / length))
            before = line[:i+1] + [(xm, ym)]
            after = [(xm, ym)] + line[i+1:]
            return before, after

    # Split point after end
    return line, []


def dash_line(line, dash_pattern, dash_offset=0):
    """
    Given a line of the form [(x, y), ...], split it according to the Qt-style
    dash pattern and offset provided. Returns a new list [[(x, y), ...], ...].
    """
    if len(dash_pattern) % 2 != 0:
        warnings.warn("Dash pattern with non-even number of lengths; "
                      "ignoring final length.")
        dash_pattern = dash_pattern[:-1]

    if not dash_pattern or len(line) <= 1:
        return [line]

    pattern_length = sum(dash_pattern)
    dash_offset %= pattern_length

    # Advance through the dash pattern according to the offset
    dash_iter = iter(izip(cycle(dash_pattern), cycle([True, False])))
    for dash_length, dash_on in dash_iter:
        if dash_length <= dash_offset:
            dash_offset -= dash_length
        else:
            dash_length -= dash_offset
            break

    out = []
    while line:
        before, line = split_line(line, dash_length)
        if dash_on:
            out.append(before)
        dash_length, dash_on = next(dash_iter)

    return out


class OutlinePaintEngine(QPaintEngine):
    """
    Used internally by OutlinePaintDevice. Accumulates stroke-drawing commands
    and records the pixel-coordinates of these line segments and colours used.
    Fetch the accumulated lines using getOutlines().
    """

    def __init__(self, paint_device):
        # NB: AllFeatures passed since doing otherwise results in unsupported
        # features being turned into rasters (which is not a useful fallback
        # here).
        super().__init__(QPaintEngine.PaintEngineFeature.AllFeatures)

        self._transform = QTransform()
        self._pen = QPen()

        # [((r, g, b, a) or None, width, [(x, y), ...]), ...]
        #
        # Colours are None or tuples of 0.0 to 1.0 floats. Line widths are
        # given in pixels. Line coordinates are given in pixels.
        self._outlines = []

    def getOutlines(self):
        """
        See OutlinePaintDevice.getOutlines(), except the line widths and
        coordinates are given in pixels.
        """
        return self._outlines

    def begin(self, paint_device):
        return True

    def end(self):
        return True

    def updateState(self, new_state):
        dirty_flags = new_state.state()
        if dirty_flags & QPaintEngine.DirtyTransform:
            self._transform = new_state.transform()
        if dirty_flags & QPaintEngine.DirtyPen:
            self._pen = new_state.pen()
        if (dirty_flags & QPaintEngine.DirtyClipEnabled or
                dirty_flags & QPaintEngine.DirtyClipRegion or
                dirty_flags & QPaintEngine.DirtyClipPath):
            # Clipping seems to be done by the QtSVG library's own renderer so
            # some time can be saved here!
            if new_state.clipOperation() != Qt.ClipOperation.NoClip:
                raise NotImplementedError(
                    "Clipping mode {} not supported".format(
                        new_state.clipOperation()))
        if dirty_flags & QPaintEngine.DirtyCompositionMode:
            # Other modes not expected (not available in SVG)
            if new_state.compositionMode() != \
                    QPainter.CompositionMode.SourceOver:
                raise NotImplementedError(
                    "CompositionMode {} not supported".format(
                        new_state.compositionMode()))

    def drawImage(self, r, pm, sr, flags):
        # Draw image outline...
        self.drawRects(r, 1)

    def drawPixmap(self, r, pm, sr):
        # Draw pixmap outline...
        self.drawRects(r, 1)

    def drawPolygon(self, points, count, mode):
        # Just draw the polygon using drawPath...
        # NB: A bug prevents a useful implementation of this function being
        # written. Fortunately the QtSVG renderer only ever uses QPainterPath
        # objects for drawing.
        raise NotImplementedError("Qt for Python bug PYSIDE-891 "
                                  "prevents drawPolygon being implemented")

        # Implementation should look something like:
        #
        #     from PySide2.QtGui import QPainterPath
        #     path = QPainterPath()
        #     for i, point in enumerate(points):
        #         if i == 0:
        #             path.moveTo(point)
        #         else:
        #             path.lineTo(point)
        #     self.drawPath(path)

    def drawPath(self, path):
        # Nothing to do if not drawing the outline
        if (self._pen.style() == Qt.PenStyle.NoPen or
                self._pen.brush().style() == Qt.BrushStyle.NoBrush):
            return

        # Determine colour
        if self._pen.brush().style() == Qt.BrushStyle.SolidPattern:
            rgba = self._pen.brush().color().getRgbF()
        else:
            rgba = None

        # Determine dash style
        pen_width = self._pen.widthF() or 1.0
        dash_pattern = [v*pen_width for v in self._pen.dashPattern()]
        dash_offset = self._pen.dashOffset() * pen_width

        # When applying the dash style, perform this on a version of the line
        # prior to the current transform (to achieve correct dash spacing)
        transform = self._transform
        inverse_transform, invertable = self._transform.inverted()
        if not invertable:
            transform = inverse_transform = QTransform()
            if dash_pattern:
                warnings.warn(
                    "Dashed lines transformed by non-singular matrices are "
                    "not supported and the dash pattern will be incorrectly "
                    "scaled.")

        # Approximate the scaling factor applied by the current transform as
        # being the scale applied to a diagonal line. This won't work if the
        # line happens to be an eigen vector but for non-uniform scalings, the
        # concept of a scaled line widthis not especially well defined anyway
        # anyway.
        #
        # (test_line has length 1)
        test_line = QLineF(0, 0, 2**0.5 / 2.0, 2**0.5 / 2.0)
        scaled_pen_width = pen_width * self._transform.map(test_line).length()

        # Don't scale the points for dashing when in cosmetic mode
        if self._pen.isCosmetic():
            transform = inverse_transform = QTransform()
            scaled_pen_width = pen_width

        # Convert to simple straight line segments. The conversion of Text,
        # Bezier curves, arcs, ellipses etc. into to chains of simple straight
        # line is implemented by QPainterPath.toSubpathPolygons. Note that the
        # transform being supplied here is important to ensure bezier-to-line
        # segmentation occurs at the correct resolution.
        for poly in path.toSubpathPolygons(self._transform):
            # Apply dash style. The coordinates must be scaled back to their
            # native size for this process since the spacing for dashes is
            # based on  the line width and aspect ratio used.
            line = [p.toTuple() for p in inverse_transform.map(poly)]
            sub_lines = dash_line(line, dash_pattern, dash_offset)

            # Transform the coordinates back to pixels once more and add colour
            # information.
            self._outlines.extend(
                (rgba, scaled_pen_width, [transform.map(*p) for p in line])
                for line in sub_lines
            )


class OutlinePaintDevice(QPaintDevice):
    """
    A QPaintDevice which, instead of actually painting, accumulates a list of
    line segments representing the outlines of all stroked shapes which can be
    fetched using ``getOutlines``.
    """

    def __init__(self, width_mm, height_mm, pixels_per_mm=5):
        """
        Create the paint device with the specified dimensions.

        Parameters
        ----------
        width_mm, height_mm : float
            The dimensions of the drawing area in milimeters.
        pixels_per_mm : float
            This argument controls the resolution with which Bezier curves are
            transformed into straight lines.

            Bezier curves are broken into straight line segments as if the
            lines were to be rasterised on a display with this may pixels per
            mm.  Higher resolutions result in greater numbers of straight line
            segments being created.
        """
        super().__init__()
        self._width = width_mm
        self._height = height_mm
        self._ppmm = pixels_per_mm

        self._paint_engine = OutlinePaintEngine(self)

    def getOutlines(self):
        """
        Return the list of straight line segments drawn to this device.

        Returns
        -------
        [((r, g, b, a) or None, width, [(x, y), ...]), ...]
            A list of polylines made up of a (colour, line) pairs.

            The 'colour' values define the colour used to draw the line, if a
            solid colour was used or None if a gradient or patterned stroke was
            used. Colours are given as four-tuples in RGBA order with values
            from 0.0 to 1.0.

            The 'width' value gives the line width used to draw the line (given
            in mm). Note that if the shape being drawn has a non-uniform
            scaling applied, this value may not be meaningful and its actual
            value should be considered undefined.

            The 'line' part of each tuple defines the outline as a series of
            (x, y) coordinates (given in mm) which describe a continuous
            polyline. These polylines may be considered open. If the first and
            last coordinate are coincident, the polyline may have been open or
            closed but this information is not retained.
        """
        # Scale line coordinates back into mm (from pixels)
        scale = 1.0 / self._ppmm
        return [
            (rgba, width*scale, [(x*scale, y*scale) for (x, y) in line])
            for (rgba, width, line) in self._paint_engine.getOutlines()
        ]

    def paintEngine(self):
        return self._paint_engine

    def metric(self, num):
        mm_per_inch = 25.4

        if num == QPaintDevice.PdmWidth:
            return self._width * self._ppmm
        elif num == QPaintDevice.PdmHeight:
            return self._height * self._ppmm
        elif num == QPaintDevice.PdmWidthMM:
            return self._width
        elif num == QPaintDevice.PdmHeightMM:
            return self._height
        elif num == QPaintDevice.PdmNumColors:
            return 2
        elif num == QPaintDevice.PdmDepth:
            return 1
        elif num == QPaintDevice.PdmDpiX:
            return mm_per_inch * self._ppmm
        elif num == QPaintDevice.PdmDpiY:
            return mm_per_inch * self._ppmm
        elif num == QPaintDevice.PdmPhysicalDpiX:
            return mm_per_inch * self._ppmm
        elif num == QPaintDevice.PdmPhysicalDpiY:
            return mm_per_inch * self._ppmm
        elif num == QPaintDevice.PdmDevicePixelRatio:
            return 1
        elif num == QPaintDevice.PdmDevicePixelRatioScaled:
            return 1
        else:
            raise NotImplementedError("Unknown metric {}".format(num))
