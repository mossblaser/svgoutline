import re

import features


class InvalidIDError(Exception):
    """Thrown when an ID is supplied which doesn't conform to the XML spec."""
    pass

class InvalidClassError(Exception):
    """Thrown when an class name is supplied."""
    pass

class InvalidXmlSpace(Exception):
    """Thrown when an xml:space is supplied which doesn't conform to the XML spec."""
    pass


def parse_ws_list(attribute):
    """Parse a whitespace delimited list into an array."""
    if attribute is None:
        return None
    else:
        return list(filter(None, re.split(r"\s+", attribute)))

def parse_comma_list(attribute):
    """Parse a comma delimited list into an array."""
    if attribute is None:
        return None
    else:
        return list(filter(None, re.split(r"\s*,\s*", attribute)))

def parse_required_features(attribute):
    """
    Parse the set of features required by an SVG. Throws a warning if some are
    not supported.
    """
    required_features = set(parse_ws_list(attribute) or [])
    
    missing_features = required_features.difference(
        features.SUPPORTED_FEATURES)
    
    if missing_features:
        warnings.warn("SVG file requires some unsupported features: {}".format(
            ", ".join(missing_features)))
    
    return required_features

def parse_required_extensions(attribute):
    """
    Parse the set of extensions required by an SVG. Throws a warning if some are
    not supported.
    """
    required_extensions = set(parse_ws_list(attribute) or [])
    
    # Non supported at the moment!
    if required_extensions:
        warnings.warn(
            "SVG file requires some unsupported extensions: {}".format(
                ", ".join(required_extensions)))
    
    return required_extensions

def parse_system_language(attribute):
    """
    Parse the system language field.
    """
    return parse_comma_list(attribute)

def parse_id(attribute):
    """Validate an ID according to the XML spec."""
    # May have no ID
    if attribute is None:
        return None
    
    # Validates against the 'Name' production rule defined in section 2.2 of
    # the XML 1.0 standard
    valid = bool(re.fullmatch(
        (
            # NameStartChar
            "(:|[A-Z]|_|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|"
            "[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|"
            "[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|"
            "[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|"
            "[\U00010000-\U000EFFFF])"
            # NameChar
            "(:|[A-Z]|_|[a-z]|[\u00C0-\u00D6]|[\u00D8-\u00F6]|"
            "[\u00F8-\u02FF]|[\u0370-\u037D]|[\u037F-\u1FFF]|"
            "[\u200C-\u200D]|[\u2070-\u218F]|[\u2C00-\u2FEF]|"
            "[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]|"
            "[\U00010000-\U000EFFFF]|-|.|[0-9]|\u00B7|[\u0300-\u036F]|"
            "[\u203F-\u2040])*"
        ),
        attribute
    ))
    
    if not valid:
        raise InvalidIDError(attribute)
    else:
        return attribute

def parse_class_name(attribute):
    """Return the list of classes defined by a 'class' attribute."""
    if attribute is None:
        return []
    else:
        classes = parse_ws_list(attribute)
        out = []
        for class_name in classes:
            try:
                out.append(parse_id(class_name))
            except InvalidIDError:
                raise InvalidClassError(class_name)
        return out

def parse_xml_base(attribute):
    # Nothing to do!
    return attribute

def parse_xml_lang(attribute):
    # Nothing to do!
    return attribute

def parse_xml_space(attribute):
    """Parse an xml:space attribute. Returns True if 'preserve', default
    otherwise."""
    if attribute == "preserve":
        return True
    elif attribute is None or attribute == "default":
        return False
    else:
        raise InvalidXmlSpace(attribute)

def unsupported(attribute, attribute_name):
    """Report when this attribute is not-none."""
    if attribute is not None:
        warnings.warn("Attribute '{}' not supported.".format(attribute_name))
