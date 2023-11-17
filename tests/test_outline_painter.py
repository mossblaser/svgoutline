import pytest

from svgoutline.outline_painter import (
    split_line,
    dash_line,
    OutlinePaintDevice,
)

from PySide6.QtGui import QPainter
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from PySide6.QtGui import QPen
from PySide6.QtGui import QBrush
from PySide6.QtGui import QGuiApplication

from PySide6.QtCore import Qt


@pytest.fixture(scope="module")
def app():
    return QGuiApplication()


class TestSplitLine(object):

    def test_empty_line(self):
        # Degenerate input case
        assert split_line([], -1) == ([], [])
        assert split_line([], 0) == ([], [])
        assert split_line([], 1) == ([], [])

    def test_point(self):
        # Degenerate input case
        assert split_line([(0, 1)], -1) == ([], [(0, 1)])
        assert split_line([(0, 1)], 0) == ([], [(0, 1)])
        assert split_line([(0, 1)], 1) == ([(0, 1)], [])

    def test_single_line_segment(self):
        # Before start
        assert split_line([(0, 0), (2, 0)], -1) == ([], [(0, 0), (2, 0)])

        # At start
        assert split_line([(0, 0), (2, 0)], 0) == ([], [(0, 0), (2, 0)])

        # Part way
        assert split_line([(0, 0), (2, 0)], 1) == (
            [(0, 0), (1, 0)],
            [(1, 0), (2, 0)],
        )

        # At end
        assert split_line([(0, 0), (2, 0)], 2) == ([(0, 0), (2, 0)], [])

        # Past end
        assert split_line([(0, 0), (2, 0)], 2) == ([(0, 0), (2, 0)], [])

    def test_multiple_line_segment(self):
        # Before start
        assert split_line([(0, 0), (2, 0), (2, 2)], -1) == (
            [], [(0, 0), (2, 0), (2, 2)])

        # At start
        assert split_line([(0, 0), (2, 0), (2, 2)], 0) == (
            [], [(0, 0), (2, 0), (2, 2)])

        # Part way through first segment
        assert split_line([(0, 0), (2, 0), (2, 2)], 1) == (
            [(0, 0), (1, 0)], [(1, 0), (2, 0), (2, 2)])

        # On midpoint
        assert split_line([(0, 0), (2, 0), (2, 2)], 2) == (
            [(0, 0), (2, 0)], [(2, 0), (2, 2)])

        # Part way through second segment
        assert split_line([(0, 0), (2, 0), (2, 2)], 3) == (
            [(0, 0), (2, 0), (2, 1)], [(2, 1), (2, 2)])

        # At end
        assert split_line([(0, 0), (2, 0), (2, 2)], 4) == (
            [(0, 0), (2, 0), (2, 2)], [])

        # Past end
        assert split_line([(0, 0), (2, 0), (2, 2)], 5) == (
            [(0, 0), (2, 0), (2, 2)], [])


class TestDashLine(object):

    @pytest.mark.parametrize("line", [[], [(0, 0)]])
    @pytest.mark.parametrize("dash_pattern", [[], [1, 1]])
    @pytest.mark.parametrize("dash_offset", [0, 1, -1])
    def test_empty_or_point_line(self, line, dash_pattern, dash_offset):
        assert dash_line(line, dash_pattern, dash_offset) == [line]

    @pytest.mark.parametrize("dash_pattern", [[], [1]])
    @pytest.mark.parametrize("dash_offset", [0, 1, -1])
    def test_solid_line(self, dash_pattern, dash_offset):
        line = [(0, 0), (1, 0), (1, 1)]

        if len(dash_pattern) == 1:
            with pytest.warns(UserWarning):
                assert dash_line(line, dash_pattern, dash_offset) == [line]
        else:
            assert dash_line(line, dash_pattern, dash_offset) == [line]

    @pytest.mark.parametrize("extraneous_dash", [False, True])
    def test_basic_dash(self, extraneous_dash):
        line = [(0, 0), (4, 0), (4, 4)]
        dash_pattern = [2, 1]
        expected = [
            [(0, 0), (2, 0)],
            [(3, 0), (4, 0), (4, 1)],
            [(4, 2), (4, 4)],
        ]
        if extraneous_dash:
            with pytest.warns(UserWarning):
                assert dash_line(line, dash_pattern + [1], 0) == expected
        else:
            assert dash_line(line, dash_pattern, 0) == expected

    def test_complex_dash(self):
        line = [(0, 0), (20, 0)]
        dash_pattern = [1, 2, 3, 4]
        expected = [
            [(0, 0), (1, 0)],
            [(3, 0), (6, 0)],
            [(10, 0), (11, 0)],
            [(13, 0), (16, 0)],
        ]
        assert dash_line(line, dash_pattern, 0) == expected

    def test_offset(self):
        # No offset (sanity check)
        assert dash_line([(0, 0), (10, 0)], [2, 3], 0) == [
            [(0, 0), (2, 0)],
            [(5, 0), (7, 0)],
        ]

        # Positive offset part-way into first dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], 1) == [
            [(0, 0), (1, 0)],
            [(4, 0), (6, 0)],
            [(9, 0), (10, 0)],
        ]

        # Positive offset into boundry between first and second dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], 2) == [
            [(3, 0), (5, 0)],
            [(8, 0), (10, 0)],
        ]

        # Positive offset into second dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], 3) == [
            [(2, 0), (4, 0)],
            [(7, 0), (9, 0)],
        ]

        # At end of second dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], 5) == [
            [(0, 0), (2, 0)],
            [(5, 0), (7, 0)],
        ]

        # Positive offset cycling around back into first dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], 6) == [
            [(0, 0), (1, 0)],
            [(4, 0), (6, 0)],
            [(9, 0), (10, 0)],
        ]

        # Negative offset cycling around back into first dash
        assert dash_line([(0, 0), (10, 0)], [2, 3], -4) == [
            [(0, 0), (1, 0)],
            [(4, 0), (6, 0)],
            [(9, 0), (10, 0)],
        ]


class TestOutlinePaintDevice(object):

    @pytest.fixture
    def width(self):
        return 100.0

    @pytest.fixture
    def height(self):
        return 200.0

    @pytest.fixture
    def ppmm(self):
        return 10.0

    @pytest.fixture
    def opd(self, app, width, height, ppmm):
        return OutlinePaintDevice(width, height, ppmm)

    @pytest.fixture
    def p(self, app, opd):
        p = QPainter(opd)
        try:
            yield p
        finally:
            p.end()

    def test_do_nothing(self, p, opd):
        assert opd.getOutlines() == []

    def test_no_pen(self, p, opd):
        pen = QPen()
        pen.setStyle(Qt.PenStyle.NoPen)
        p.setPen(pen)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(10, 20)
        p.drawPath(path)

        assert opd.getOutlines() == []

    def test_no_brush(self, p, opd):
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.NoBrush)
        pen = QPen()
        pen.setBrush(brush)
        p.setPen(pen)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(10, 20)
        p.drawPath(path)

    def test_simple_path(self, p, opd):
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(10, 20)
        p.drawPath(path)

        assert opd.getOutlines() == [
            ((0.0, 0.0, 0.0, 1.0), 0.1, [(0.0, 0.0), (1.0, 2.0)]),
        ]

    def test_transformed_path(self, p, opd):
        p.scale(10, 10)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(1, 2)
        p.drawPath(path)

        assert opd.getOutlines() == [
            ((0.0, 0.0, 0.0, 1.0), 1.0, [(0.0, 0.0), (1.0, 2.0)]),
        ]

    def test_singular_transformed_path(self, p, opd):
        p.scale(10, 0)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(1, 2)
        p.drawPath(path)

        out = opd.getOutlines()
        assert len(out) == 1
        colour, width, lines = out[0]
        assert colour == (0.0, 0.0, 0.0, 1.0)
        assert lines == [(0.0, 0.0), (1.0, 0.0)]

    def test_singular_transformed_path_with_dashes(self, p, opd):
        with pytest.warns(UserWarning):
            pen = QPen()
            pen.setDashPattern([2, 1])
            pen.setWidth(5)
            p.setPen(pen)

            p.scale(10, 0)
            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(1, 2)
            p.drawPath(path)

            out = opd.getOutlines()
            assert len(out) == 1
            colour, width, lines = out[0]
            assert colour == (0.0, 0.0, 0.0, 1.0)
            assert lines == [(0.0, 0.0), (1.0, 0.0)]

    def test_colours(self, p, opd):
        p.setPen(QColor(255, 0, 0))
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(10, 0)
        p.drawPath(path)

        p.setPen(QColor(0, 255, 0))
        path = QPainterPath()
        path.moveTo(0, 10)
        path.lineTo(10, 10)
        p.drawPath(path)

        p.setPen(QColor(0, 0, 255))
        path = QPainterPath()
        path.moveTo(0, 20)
        path.lineTo(10, 20)
        p.drawPath(path)

        p.setPen(QColor(0, 0, 0, 128))
        path = QPainterPath()
        path.moveTo(0, 30)
        path.lineTo(10, 30)
        p.drawPath(path)

        # Non-solid brush (colour should be nullified)
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.CrossPattern)
        pen = QPen()
        pen.setBrush(brush)
        p.setPen(pen)
        path = QPainterPath()
        path.moveTo(0, 40)
        path.lineTo(10, 40)
        p.drawPath(path)

        assert opd.getOutlines() == [
            ((1.0, 0.0, 0.0, 1.0), 0.1, [(0.0, 0.0), (1.0, 0.0)]),
            ((0.0, 1.0, 0.0, 1.0), 0.1, [(0.0, 1.0), (1.0, 1.0)]),
            ((0.0, 0.0, 1.0, 1.0), 0.1, [(0.0, 2.0), (1.0, 2.0)]),
            ((0.0, 0.0, 0.0, 128/255.), 0.1, [(0.0, 3.0), (1.0, 3.0)]),
            (None, 0.1, [(0.0, 4.0), (1.0, 4.0)]),
        ]

    def test_simple_dashes(self, p, opd):
        pen = QPen()
        pen.setDashPattern([2, 1])
        pen.setWidth(5)
        p.setPen(pen)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(30, 0)
        p.drawPath(path)

        assert opd.getOutlines() == [
            ((0.0, 0.0, 0.0, 1.0), 0.5, [(0.0, 0.0), (1.0, 0.0)]),
            ((0.0, 0.0, 0.0, 1.0), 0.5, [(1.5, 0.0), (2.5, 0.0)]),
        ]

    def test_simple_dashes_offset(self, p, opd):
        pen = QPen()
        pen.setDashPattern([2, 1])
        pen.setDashOffset(1)
        pen.setWidth(5)
        p.setPen(pen)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(30, 0)
        p.drawPath(path)

        assert opd.getOutlines() == [
            ((0.0, 0.0, 0.0, 1.0), 0.5, [(0.0, 0.0), (0.5, 0.0)]),
            ((0.0, 0.0, 0.0, 1.0), 0.5, [(1.0, 0.0), (2.0, 0.0)]),
            ((0.0, 0.0, 0.0, 1.0), 0.5, [(2.5, 0.0), (3.0, 0.0)]),
        ]

    def test_dashes_scaled(self, p, opd):
        pen = QPen()
        pen.setDashPattern([1, 1])
        pen.setWidthF(2**0.5)
        p.setPen(pen)

        p.scale(10, 20)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(3, 3)
        p.drawPath(path)

        assert [(colour, lines)
                for (colour, width, lines) in opd.getOutlines()] == [
            ((0.0, 0.0, 0.0, 1.0), [(0.0, 0.0), (1.0, 2.0)]),
            ((0.0, 0.0, 0.0, 1.0), [(2.0, 4.0), (3.0, 6.0)]),
        ]

    def test_cosmetic_pen_with_dashes(self, p, opd):
        pen = QPen()
        pen.setDashPattern([2, 1])
        pen.setCosmetic(True)
        pen.setWidth(5)
        p.setPen(pen)

        p.scale(10, 10)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(3, 0)
        p.drawPath(path)

        assert [(colour, lines)
                for (colour, width, lines) in opd.getOutlines()] == [
            ((0.0, 0.0, 0.0, 1.0), [(0.0, 0.0), (1.0, 0.0)]),
            ((0.0, 0.0, 0.0, 1.0), [(1.5, 0.0), (2.5, 0.0)]),
        ]

    def test_bezier_resolution(self, p, opd):
        # Two beziers drawn at different sizes should be interpolated to
        # different levels of detail
        path = QPainterPath()
        path.moveTo(0, 0)
        path.quadTo(100, 10, 10, 20)
        p.drawPath(path)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.quadTo(10, 1, 1, 2)
        p.drawPath(path)

        lines = opd.getOutlines()
        assert len(lines) == 2
        colour_0, width_0, line_0 = lines[0]
        colour_1, width_1, line_1 = lines[1]

        assert len(line_0) > 2
        assert len(line_1) > 2
        assert len(line_0) > len(line_1)

    def test_bezier_resolution_after_transform(self, p, opd):
        # Two beziers which are the same size after transformation should be
        # interpolated to the same level of detail
        path = QPainterPath()
        path.moveTo(0, 0)
        path.quadTo(100, 10, 10, 20)
        p.drawPath(path)

        p.scale(10, 10)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.quadTo(10, 1, 1, 2)
        p.drawPath(path)

        lines = opd.getOutlines()
        assert len(lines) == 2
        colour_0, width_0, line_0 = lines[0]
        colour_1, width_1, line_1 = lines[1]

        assert len(line_0) > 2
        assert len(line_0) == len(line_1)

    def test_text(self, p, opd):
        font = QFont()
        path = QPainterPath()
        path.addText(0, 0, font, "T")
        p.drawPath(path)

        lines = opd.getOutlines()
        assert len(lines) == 1
