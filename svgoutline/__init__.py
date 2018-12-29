import sys
import xml.etree.ElementTree as ET

import attributes

SVG_NAMESPACE = "http://www.w3.org/2000/svg"

def read_xml_file(filename, ignored_namespaces=[SVG_NAMESPACE]):
    """
    Parse the provided XML file and return a
    :py:class:`xml.etree.ElementTree.Element`. Strips namespaces listed in
    the ``ignored_namespaces`` argument.
    """
    bracketed_namespaces = ["{{{}}}".format(ns) for ns in ignored_namespaces]
    
    with open(filename) as f:
        parser = ET.iterparse(f)
        for _, element in parser:
            for namespace in bracketed_namespaces:
                if element.tag.startswith(namespace):
                    element.tag = element.tag[len(namespace):]
    
    return parser.root





class Container(object):
    """A container, such as a Group (<g>) or svg element (<svg>)."""
    
    def __init__(self, elements=[], transform=None):
        self.elements = elements
        self.transform = transform


class SVG(Container):
    """An <svg> container."""

class G(Container):
    """A <g> (group) container."""


root = read_xml_file(sys.argv[1])

# Conditional processing attributes
required_features = attributes.parse_required_features(root.attrib.get("requiredFeatures"))
required_extensions = attributes.parse_required_extensions(root.attrib.get("requiredExtensions"))
system_language = attributes.parse_system_language(root.attrib.get("systemLanguage"))

# Core attributes
id = attributes.parse_id(root.attrib.get("id"))
xml_base = attributes.parse_xml_base(root.attrib.get("xml:base"))
xml_lang = attributes.parse_xml_lang(root.attrib.get("xml:lang"))
xml_sapce = attributes.parse_xml_space(root.attrib.get("xml:space"))

# Document event attributes
for attribute in ["onunload", "onabort", "onerror",
                  "onresize", "onscroll", "onzoom"]:
    attributes.unsupported(root.attrib.get(attribute), attribute)

# Graphical event attributes
for attribute in ["onfocusin", "onfocusout", "onactivate", "onclick",
                  "onmousedown", "onmouseup", "onmouseover", "onmousemove",
                  "onmouseout", "onload"]:
    attributes.unsupported(root.attrib.get(attribute), attribute)

# <svg> specific attributes
class_name = attributes.parse_class_name(root.attrib.get("class"))

print("Tag:", root.tag)
print("Attrib:", root.attrib)
print("Children:", list(root))
print("Class:", class_name)
