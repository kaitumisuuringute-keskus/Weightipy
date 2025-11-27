"""
Type definitions for weightipy weighting schemes.

This module defines the core type aliases and TypedDict classes used throughout
weightipy for type checking and documentation purposes.
"""

from typing import Any, Dict, Mapping, TypedDict, Union


SimpleSchemeDict = Dict[str, Dict[Any, Union[float, int]]]
"""
Type alias for a simple (flat) weighting scheme dictionary.

Maps dimension names (e.g., 'age', 'gender') to their target distributions,
where each distribution is a dictionary mapping categories to their target
proportions or counts.

Examples
--------
>>> scheme: SimpleSchemeDict = {
...     "age": {"18-24": 10.0, "25-34": 20.0, "35+": 70.0},
...     "gender": {"Male": 48.0, "Female": 52.0}
... }
"""


class SegmentedSchemeDict(TypedDict):
    """
    TypedDict for a segmented (nested) weighting scheme.
    
    Used when you want to apply different weighting targets to different segments
    of your data (e.g., different regions, time periods, or demographic groups).
    
    Attributes
    ----------
    segment_by : str
        Name of the column to segment by (e.g., 'region', 'country')
    segment_targets : Mapping[str, float]
        Target proportions for each segment. Maps segment names to their
        target proportions (e.g., {"East": 40.0, "West": 60.0})
    segments : Mapping[str, SimpleSchemeDict]
        Weighting schemes for each segment. Maps segment names to their
        individual SimpleSchemeDict definitions
    
    Examples
    --------
    >>> scheme: SegmentedSchemeDict = {
    ...     "segment_by": "region",
    ...     "segment_targets": {"North": 40.0, "South": 60.0},
    ...     "segments": {
    ...         "North": {
    ...             "age": {"18-24": 15.0, "25+": 85.0},
    ...             "gender": {"Male": 50.0, "Female": 50.0}
    ...         },
    ...         "South": {
    ...             "age": {"18-24": 10.0, "25+": 90.0},
    ...             "gender": {"Male": 48.0, "Female": 52.0}
    ...         }
    ...     }
    ... }
    """
    segment_by: str
    segment_targets: Mapping[str, float]
    segments: Mapping[str, SimpleSchemeDict]


SchemeDict = Union[SimpleSchemeDict, SegmentedSchemeDict]
"""
Type alias for any valid weighting scheme dictionary.

Can be either a SimpleSchemeDict (flat) or SegmentedSchemeDict (nested).
This is the main type used by functions that accept scheme definitions.
"""


__all__ = [
    "SimpleSchemeDict", "SegmentedSchemeDict", "SchemeDict"
]