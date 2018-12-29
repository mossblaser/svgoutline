"""
Code for testing feature support via the 'requiredFeatures' attribute of the
<svg> tag.
"""

from functools import partial

"""
The set SVG features supported by this implementation.
"""
SUPPORTED_FEATURES = set([
    # ‘id’, ‘xml:base’, ‘xml:lang’ and ‘xml:space’ attributes
    "http://www.w3.org/TR/SVG11/feature#CoreAttribute",
    # ‘svg’, ‘g’, ‘defs’, ‘desc’, ‘title’, ‘metadata’, ‘symbol’ and ‘use’ elements
    "http://www.w3.org/TR/SVG11/feature#Structure",
    # as above but without 'symbol' elements.
    "http://www.w3.org/TR/SVG11/feature#BasicStructure",
    # 'enable-background' attribyute
    "http://www.w3.org/TR/SVG11/feature#ContainerAttribute",
    # the ‘switch’ element, and the ‘requiredFeatures’, ‘requiredExtensions’
    # and ‘systemLanguage’ attributes
    "http://www.w3.org/TR/SVG11/feature#ConditionalProcessing",
    # 'image' element
    "http://www.w3.org/TR/SVG11/feature#Image",
    # 'style' element
    "http://www.w3.org/TR/SVG11/feature#Style",
    # 'clip' and 'overflow' properties
    "http://www.w3.org/TR/SVG11/feature#ViewportAttribute",
    # ‘rect’, ‘circle’, ‘line’, ‘polyline’, ‘polygon’, ‘ellipse’ and ‘path’
    # elements
    "http://www.w3.org/TR/SVG11/feature#Shape",
    # ‘text’, ‘tspan’, ‘tref’, ‘textPath’, ‘altGlyph’, ‘altGlyphDef’,
    # ‘altGlyphItem’ and ‘glyphRef’ elements
    "http://www.w3.org/TR/SVG11/feature#Text",
    # just the 'text' element
    "http://www.w3.org/TR/SVG11/feature#BasicText",
    # ‘color’, ‘fill’, ‘fill-rule’, ‘stroke’, ‘stroke-dasharray’,
    # ‘stroke-dashoffset’, ‘stroke-linecap’, ‘stroke-linejoin’,
    # ‘stroke-miterlimit’, ‘stroke-width’, ‘color-interpolation’ and
    # ‘color-rendering’ properties
    "http://www.w3.org/TR/SVG11/feature#PaintAttribute",
    # ‘color’, ‘fill’, ‘fill-rule’, ‘stroke’, ‘stroke-dasharray’,
    # ‘stroke-dashoffset’, ‘stroke-linecap’, ‘stroke-linejoin’,
    # ‘stroke-miterlimit’, ‘stroke-width’ and ‘color-rendering’ properties
    "http://www.w3.org/TR/SVG11/feature#BasicPaintAttribute",
    # ‘opacity’, ‘stroke-opacity’ and ‘fill-opacity’ properties
    "http://www.w3.org/TR/SVG11/feature#OpacityAttribute",
    # ‘display’, ‘image-rendering’, ‘pointer-events’, ‘shape-rendering’,
    # ‘text-rendering’ and ‘visibility’ properties
    "http://www.w3.org/TR/SVG11/feature#GraphicsAttribute",
    # ‘display’ and ‘visibility’ properties
    "http://www.w3.org/TR/SVG11/feature#BasicGraphicsAttribute",
    # ‘marker’ element
    "http://www.w3.org/TR/SVG11/feature#Marker",
    # ‘color-profile’ element
    "http://www.w3.org/TR/SVG11/feature#ColorProfile",
    # ‘linearGradient’, ‘radialGradient’ and ‘stop’ elements
    "http://www.w3.org/TR/SVG11/feature#Gradient",
    # 'pattern' element
    "http://www.w3.org/TR/SVG11/feature#Pattern",
    # ‘clipPath’ element and the ‘clip-path’ and ‘clip-rule’ properties
    "http://www.w3.org/TR/SVG11/feature#Clip",
    # ‘clipPath’ element and the ‘clip-path’ property
    "http://www.w3.org/TR/SVG11/feature#BasicClip",
    # 'mask' element
    "http://www.w3.org/TR/SVG11/feature#Mask",
    # ‘filter’, ‘feBlend’, ‘feColorMatrix’, ‘feComponentTransfer’,
    # ‘feComposite’, ‘feConvolveMatrix’, ‘feDiffuseLighting’,
    # ‘feDisplacementMap’, ‘feFlood’, ‘feGaussianBlur’, ‘feImage’, ‘feMerge’,
    # ‘feMergeNode’, ‘feMorphology’, ‘feOffset’, ‘feSpecularLighting’,
    # ‘feTile’, ‘feDistantLight’, ‘fePointLight’, ‘feSpotLight’, ‘feFuncR’,
    # ‘feFuncG’, ‘feFuncB’ and ‘feFuncA’ elements
    "http://www.w3.org/TR/SVG11/feature#Filter",
    # ‘filter’, ‘feBlend’, ‘feColorMatrix’, ‘feComponentTransfer’,
    # ‘feComposite’, ‘feFlood’, ‘feGaussianBlur’, ‘feImage’, ‘feMerge’,
    # ‘feMergeNode’, ‘feOffset’, ‘feTile’, ‘feFuncR’, ‘feFuncG’, ‘feFuncB’ and
    # ‘feFuncA’ elements
    "http://www.w3.org/TR/SVG11/feature#BasicFilter",
    # ‘xlink:type’, ‘xlink:href’, ‘xlink:role’, ‘xlink:arcrole’, ‘xlink:title’,
    # ‘xlink:show’ and ‘xlink:actuate’ attributes
    "http://www.w3.org/TR/SVG11/feature#XlinkAttribute",
    # ‘externalResourcesRequired’ attribute
    "http://www.w3.org/TR/SVG11/feature#ExternalResourcesRequired",
    # ‘view’ element
    "http://www.w3.org/TR/SVG11/feature#View",
    # ‘font’, ‘font-face’, ‘glyph’, ‘missing-glyph’, ‘hkern’, ‘vkern’,
    # ‘font-face-src’, ‘font-face-uri’, ‘font-face-format’ and ‘font-face-name’
    # elements
    "http://www.w3.org/TR/SVG11/feature#Font",
    # ‘font’, ‘font-face’, ‘glyph’, ‘missing-glyph’, ‘hkern’, ‘vkern’,
    # ‘font-face-src’, ‘font-face-uri’, ‘font-face-format’ and ‘font-face-name’
    # elements
    "http://www.w3.org/TR/SVG11/feature#Font",
    # ‘font’, ‘font-face’, ‘glyph’, ‘missing-glyph’, ‘hkern’, ‘vkern’,
    # ‘font-face-src’, ‘font-face-uri’, ‘font-face-format’ and ‘font-face-name’
    # elements
    "http://www.w3.org/TR/SVG11/feature#Font",
    # ‘foreignObject’ element
    "http://www.w3.org/TR/SVG11/feature#Extensibility",
    # SVG 1.0 feature: All of the following are supported:
    # * Basic Data Types and Interfaces
    # * Document Structure
    # * Styling
    # * Coordinate Systems, Transformations and Units
    # * Paths
    # * Basic Shapes
    # * Text
    # * Painting: Filling, Stroking and Marker Symbols
    # * Color
    # * Gradients and Patterns
    # * Clipping, Masking and Compositing
    # * Filter Effects
    # * Fonts
    # * The ‘switch’ element
    # * The ‘requiredFeatures’ attribute
    # * The ‘requiredExtensions’ attribute
    # * The ‘systemLanguage’ attribute
    "org.w3c.svg.static",
    # 'Meta features' (i.e. features defined in terms of combinations of other
    # features) are added later.
])


def supports(feature):
    """
    Test whether a feature name is supported by this implementation.
    """
    return feature in SUPPORTED_FEATURES

def supports_one_of(iterable):
    """
    Test whether at least one of the named features is supported by this
    implementation.
    """
    return bool(SUPPORTED_FEATURES.intersection(set(iterable)))

def supports_all_of(iterable):
    """
    Test whether all of the named features are supported by this
    implementation.
    """
    return set(iterable).issubset(SUPPORTED_FEATURES)


# If-this-then-that rules in the form of tuples (feature, test_fn).  If
# 'test_fn' returns true, 'feature' will be added to SUPPORTED_FEATURES.
SUPPORTS_FEATURE_IF = [
    ("http://www.w3.org/TR/SVG11/feature#SVG",
     partial(supports_one_of,
             ["http://www.w3.org/TR/SVG11/feature#SVG-static",
              "http://www.w3.org/TR/SVG11/feature#SVG-animation",
              "http://www.w3.org/TR/SVG11/feature#SVG-dynamic",
              "http://www.w3.org/TR/SVG11/feature#SVGDOM"])),
    ("http://www.w3.org/TR/SVG11/feature#SVGDOM",
     partial(supports_one_of,
             ["http://www.w3.org/TR/SVG11/feature#SVGDOM-static",
              "http://www.w3.org/TR/SVG11/feature#SVGDOM-animation",
              "http://www.w3.org/TR/SVG11/feature#SVGDOM-dynamic"])),
    ("http://www.w3.org/TR/SVG11/feature#SVG-static",
     partial(supports_all_of,
             ["http://www.w3.org/TR/SVG11/feature#CoreAttribute",
              "http://www.w3.org/TR/SVG11/feature#Structure",
              "http://www.w3.org/TR/SVG11/feature#ContainerAttribute",
              "http://www.w3.org/TR/SVG11/feature#ConditionalProcessing",
              "http://www.w3.org/TR/SVG11/feature#Image",
              "http://www.w3.org/TR/SVG11/feature#Style",
              "http://www.w3.org/TR/SVG11/feature#ViewportAttribute",
              "http://www.w3.org/TR/SVG11/feature#Shape",
              "http://www.w3.org/TR/SVG11/feature#Text",
              "http://www.w3.org/TR/SVG11/feature#PaintAttribute",
              "http://www.w3.org/TR/SVG11/feature#OpacityAttribute",
              "http://www.w3.org/TR/SVG11/feature#GraphicsAttribute",
              "http://www.w3.org/TR/SVG11/feature#Marker",
              "http://www.w3.org/TR/SVG11/feature#ColorProfile",
              "http://www.w3.org/TR/SVG11/feature#Gradient",
              "http://www.w3.org/TR/SVG11/feature#Pattern",
              "http://www.w3.org/TR/SVG11/feature#Clip",
              "http://www.w3.org/TR/SVG11/feature#Mask",
              "http://www.w3.org/TR/SVG11/feature#Filter",
              "http://www.w3.org/TR/SVG11/feature#XlinkAttribute",
              "http://www.w3.org/TR/SVG11/feature#Font",
              "http://www.w3.org/TR/SVG11/feature#Extensibility"])),
    ("org.w3c.svg",
     partial(supports_one_of,
             ["org.w3c.svg.static",
              "org.w3c.svg.animation",
              "org.w3c.svg.dynamic",
              "org.w3c.dom.svg"])),
    ("org.w3c.dom.svg",
     partial(supports_one_of,
             ["org.w3c.dom.svg.static",
              "org.w3c.dom.svg.animation",
              "org.w3c.dom.svg.dynamic"])),
]

# Run through the feature support testing list repeatedly until no further
# changes are made.
changed = True
while changed:
    old_len = len(SUPPORTED_FEATURES)
    for feature, test in SUPPORTS_FEATURE_IF:
        if test():
            SUPPORTED_FEATURES.add(feature)
    changed = old_len != len(SUPPORTED_FEATURES)

"""
SVG features explicitly and intentionally *NOT* supported by this library.
"""
UNSUPPORTED_FEATURES = set([
    # Animation not supported
    "http://www.w3.org/TR/SVG11/feature#SVG-animation",
    "http://www.w3.org/TR/SVG11/feature#Animation",
    "org.w3c.svg.animation",
    # Dynamic features (e.g. links and animation) not supported
    "http://www.w3.org/TR/SVG11/feature#SVG-dynamic",
    "http://www.w3.org/TR/SVG11/feature#Hyperlinking",
    "org.w3c.svg.dynamic",
    # DOM APIs not applicable since no API is provided
    "http://www.w3.org/TR/SVG11/feature#SVGDOM-static",
    "http://www.w3.org/TR/SVG11/feature#SVGDOM-animation",
    "http://www.w3.org/TR/SVG11/feature#SVGDOM-dynamic",
    "org.w3c.dom.svg.static",
    "org.w3c.dom.svg.animation",
    "org.w3c.dom.svg.all",
    # Event APIs (e.g. 'onclick')
    "http://www.w3.org/TR/SVG11/feature#DocumentEventsAttribute",
    "http://www.w3.org/TR/SVG11/feature#GraphicalEventsAttribute",
    "http://www.w3.org/TR/SVG11/feature#AnimationEventsAttribute",
    # Custom mouse cursors
    "http://www.w3.org/TR/SVG11/feature#Cursor",
    # Scripting
    "http://www.w3.org/TR/SVG11/feature#Script",
    # All SVG 1.0 features will not be supported
    "org.w3c.svg.all",
])
