"""
Created on 13 Mar 2012

@author: rudi
"""


class NoCurrentLayerException(Exception):
    """
    Raised if no layer is selected for the tool to operate on.
    """
    pass


class IncorrectLayerTypeException(Exception):
    """
    Raised if the selected layer is of an inappropriate type.
    """
    pass


class OldSymbologyException(Exception):
    """
    Raised if the layer is using old symbology, which is not supported.
    """
    pass


class UnknownSymbolTypeException(Exception):
    """
    Raised if the symbol type is unknown.
    """
    pass


class CoordinateProcessingException(Exception):
    """
    Raised if there is an error while processing coordinates.
    """
    pass


class LayerLoadException(Exception):
    """
    Raised if a layer fails to load.
    """
    pass


class NoSelectedFeatureException(Exception):
    """
    Raised if no feature is selected.
    """
    pass


class aException(Exception):
    """
    Raised if
    """
    pass
