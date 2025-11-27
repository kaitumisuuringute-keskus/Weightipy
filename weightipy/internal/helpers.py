
from weightipy.types import SimpleSchemeDict


def _normalize_simple_dict(distributions: SimpleSchemeDict) -> SimpleSchemeDict:
    """
    Normalize a simple distribution dictionary to sum to 100%.
    
    Returns a new dictionary to avoid mutating input.

    Parameters
    ----------
    distributions : SimpleSchemeDict
        Dictionary mapping dimension names to target distributions

    Returns
    -------
    SimpleSchemeDict
        Normalized dictionary where each distribution sums to 100%

    Raises
    ------
    ValueError
        If any dimension has a total weight of zero
    """
    normalized = {}
    for dim, dist in distributions.items():
        total = sum(dist.values())
        if total == 0:
            raise ValueError(f"Total weight for dimension '{dim}' is zero.")
        normalized[dim] = {k: (v / total * 100) for k, v in dist.items()}
    return normalized

def _is_numeric_str(s: str) -> bool:
    """
    Check if a string represents a number (float or int).

    Parameters
    ----------
    s : str
        The string to check

    Returns
    -------
    bool
        True if the string can be converted to a float, False otherwise
    """
    try:
        float(s)
        return True
    except ValueError:
        return False