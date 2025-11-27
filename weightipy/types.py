from typing import Any, Dict, Mapping, TypedDict, Union


SimpleSchemeDict = Dict[str, Dict[Any, Union[float, int]]]

class SegmentedSchemeDict(TypedDict):
    segment_by: str
    segment_targets: Mapping[str, float]   # {"EE": 31.4, "LV": ...}
    segments: Mapping[str, SimpleSchemeDict]

SchemeDict = Union[SimpleSchemeDict, SegmentedSchemeDict]
