"""
A library for converting outlines (strokes) in SVG files into straight line
segments for use with pen plotters or vinyl cutting machines.
"""

from .version import __version__  # noqa: F401
from .svg_utils import get_svg_page_size  # noqa: F401
from .svg_to_outlines import svg_to_outlines  # noqa: F401
