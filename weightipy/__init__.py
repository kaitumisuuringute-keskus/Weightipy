import random
from numbers import Number
from typing import Dict, Mapping, TypedDict, Union, Optional, List, Any, cast

import pandas as pd

from weightipy.rim import Rim
from weightipy.version import version as __version__
from weightipy.weight_engine import WeightEngine


# Types

SimpleSchemeDict = Dict[str, Dict[Any, Union[float, int]]]

class SegmentedSchemeDict(TypedDict):
    segment_by: str
    segment_targets: Mapping[str, float]   # {"EE": 31.4, "LV": ...}
    segments: Mapping[str, SimpleSchemeDict]

SchemeDict = Union[SimpleSchemeDict, SegmentedSchemeDict]


# Helpers


def _normalize_simple_dict(distributions: SimpleSchemeDict) -> SimpleSchemeDict:
    """
    Normalize a simple distribution dictionary to sum to 100%.
    Returns a new dictionary to avoid mutating input.
    """
    normalized = {}
    for dim, dist in distributions.items():
        total = sum(dist.values())
        if total == 0:
            raise ValueError(f"Total weight for dimension '{dim}' is zero.")
        normalized[dim] = {k: (v / total * 100) for k, v in dist.items()}
    return normalized

def _is_numeric_str(s: str) -> bool:
    """Check if a string represents a number (float or int)."""
    try:
        float(s)
        return True
    except ValueError:
        return False




# Code

def weight(df: pd.DataFrame, scheme: Rim, verbose=False) -> pd.Series:
    """
    Weight a dataframe using a Rim scheme. The dataframe must have
    a column for each dimension in the scheme. String columns are
    automatically converted to categorical, allowing easier processing.

    Args:
        df:
        scheme:

    Returns:

    """
    df = df.copy()
    df["__identity__"] = range(len(df))

    # Convert weight columns to categories
    cols_weight = []
    for _, group in scheme.groups.items():
        for d in group["targets"]:
            col = list(d.keys())[0]
            cols_weight.append(col)

    for col in cols_weight:
        df[col] = df[col].astype("category")

    engine = WeightEngine(data=df)
    engine.add_scheme(scheme=scheme, key="__identity__", verbose=verbose)
    engine.run()
    df_weighted = engine.dataframe()
    return df_weighted[f"weights_{scheme.name}"]

def weight_dataframe(df: pd.DataFrame, scheme: Rim, weight_column="weights", verbose=False) -> pd.DataFrame:
    """
    Weight a dataframe using a Rim scheme. The dataframe must have
    a column for each dimension in the scheme. String columns are
    automatically converted to categorical, allowing easier processing.

    Args:
        df:
        scheme:
        weight_column:

    Returns:

    """
    df = df.copy()
    df["__identity__"] = range(len(df))

    # Convert weight columns to categories
    cols_weight = []
    for _, group in scheme.groups.items():
        for d in group["targets"]:
            col = list(d.keys())[0]
            cols_weight.append(col)

    for col in cols_weight:
        df[col] = df[col].astype("category")

    engine = WeightEngine(data=df)
    engine.add_scheme(scheme=scheme, key="__identity__", verbose=verbose)
    engine.run()
    df_weighted = engine.dataframe()
    del df_weighted["__identity__"]
    col_weights = f"weights_{scheme.name}"
    df_weighted = df_weighted.rename(columns={col_weights: weight_column})
    return df_weighted

weight_df = weight_dataframe


def weighting_efficiency(weights: pd.Series) -> float:
    sws = (weights.sum()) ** 2
    ssw = (weights ** 2).sum()
    return (sws / len(weights)) / ssw * 100


def scheme_from_dict(
    distributions: SchemeDict,
    name: Optional[str] = None,
    rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim scheme from a dictionary. Supports two formats:
    
    1. Simple Scheme (Flat):
       {
         "age": {"18-24": 10, "25+": 90},
         "gender": {"M": 48, "F": 52}
       }
       
    2. Segmented Scheme (Nested):
       {
         "segment_by": "region",
         "segment_targets": {"A": 30, "B": 70},
         "segments": {
            "A": { "age": {...}, "gender": {...} },
            "B": { ... }
         }
       }

    Args:
        distributions: Dictionary definition of the scheme
        name: Name of the schema
        rim_params: Parameters for the Rim class

    Returns:
        Rim: A configured Rim object
    """
    if rim_params is None:
        rim_params = {}
    if name is None:
        name = "generated_" + str(random.randint(0, 1000000))

    scheme = Rim(name, **rim_params)

    if "segment_by" in distributions and "segments" in distributions:
        config = cast(SegmentedSchemeDict, distributions)
        segment_col = config["segment_by"]
        
        # Normalize and prepare the global segment weights (e.g., EE vs LV)
        raw_seg_targets = config["segment_targets"]
        total_seg_weight = sum(raw_seg_targets.values())
        
        if total_seg_weight == 0:
            raise ValueError("Sum of 'segment_targets' cannot be zero.")

        # Calculate global targets (e.g. {'EE': 31.4, 'LV': 32.7...}) normalized to 100
        final_group_targets = {
            k: (v / total_seg_weight * 100) for k, v in raw_seg_targets.items()
        }

        for seg_key, sub_distributions in config["segments"].items():
            normalized_sub = _normalize_simple_dict(sub_distributions)
            
            # Convert to the list-of-dicts format required by Rim.add_group
            # Format: [{"age": {...}}, {"gender": {...}}]
            rim_target_list = [
                {dim: dist} for dim, dist in normalized_sub.items()
            ]

            if _is_numeric_str(seg_key):
                filter_def = f"(`{segment_col}` == '{seg_key}' or `{segment_col}` == {seg_key})"
            else:
                filter_def = f"`{segment_col}` == '{seg_key}'"

            scheme.add_group(
                name=seg_key,  # This name must match keys in final_group_targets
                filter_def=filter_def,
                targets=rim_target_list
            )

        scheme.group_targets(final_group_targets)

    else:
        flat = cast(SimpleSchemeDict, distributions)
        flat = _normalize_simple_dict(flat)

        global_targets = []
        for dim, dist in flat.items():
            global_targets.append({dim: dist})

        scheme.set_targets(
            targets=global_targets, 
            group_name="global_group"
        )

    return scheme


def scheme_dict_from_df(
    df: pd.DataFrame,
    cols_weighting: List[str],
    col_freq: str,
    col_filter: Optional[str] = None
) -> SchemeDict:
    """
    Extracts a weighting scheme dict from a reference microdata dataframe (row-per-record).

    This is useful when you have a representative dataset (e.g., Census microdata 
    or a high-quality random sample) where every row represents the combination of all demographic features, 
    and you want to calculate targets dynamically based on its distributions.

    Expected Input Format (Microdata):
    | Age   | Gender | Region | Weight/Freq |
    | 18-24 | Male   | East   | 1.0         |
    | 25-34 | Female | East   | 1.0         |
    | 65+   | Male   | West   | 2.5         |

    Args:
        df: The reference dataframe containing combinations of all demographic features.
        cols_weighting: List of columns to calculate targets for (e.g. ['Age', 'Gender']).
        col_freq: Column containing the weight or frequency of each row. 
                  (For raw census data, this is often a column of 1s).
        col_filter: Optional column for segmentation (e.g. 'Region').
                    If provided, targets are calculated within each unique value of this column.

    Returns:
        SchemeDict
    """
    if col_filter is None:
        distributions: SimpleSchemeDict = {}
        for col in cols_weighting:
            # Group by target column and sum the weights/frequencies
            # resulting in { "Male": 1500, "Female": 1600 }
            dist = df.groupby(col, observed=True)[col_freq].sum().to_dict()
            distributions[col] = dist
        return distributions

    else:
        # Pre-calculate the groups to avoid filtering the DF repeatedly
        grouped = df.groupby(col_filter, observed=True)
        
        segment_targets = {}
        segments = {}

        for seg_key, df_seg in grouped:
            # Convert key to string to ensure JSON compatibility
            # This ensures integers (e.g. region 1) become "1"
            seg_key_str = str(seg_key)

            # A. Calculate Global Target for this segment (e.g., total pop in EE)
            total_seg_weight = df_seg[col_freq].sum()
            segment_targets[seg_key_str] = total_seg_weight

            # B. Calculate Inner Targets for this segment
            inner_dists = {}
            for col in cols_weighting:
                dist = df_seg.groupby(col, observed=True)[col_freq].sum().to_dict()
                inner_dists[col] = dist
            
            segments[seg_key_str] = inner_dists

        result: SegmentedSchemeDict = {
            "segment_by": col_filter,
            "segment_targets": segment_targets,
            "segments": segments
        }
        return result
    
def scheme_dict_from_long_df(
    df: pd.DataFrame,
    col_variable: str,
    col_category: str,
    col_value: str,
    col_filter: Optional[str] = None
) -> SchemeDict:
    """
    Extracts a weighting scheme dict from a 'Long' or 'Tidy' aggregate dataframe.
    
    This is useful for census data where you have a table of totals rather 
    than individual rows.
    
    Expected Input Format:
    | Variable | Category | Value | (Optional Filter/Region) |
    | Age      | 18-24    | 500   | East                     |
    | Gender   | Male     | 480   | East                     |

    Args:
        df: The dataframe containing aggregate targets.
        col_variable: Column name identifying the dimension (e.g. 'Age', 'Gender')
        col_category: Column name identifying the group (e.g. '18-24', 'Male')
        col_value: Column name identifying the target weight/count.
        col_filter: Optional column for segmentation (e.g. 'Region')

    Returns:
        SchemeDict
    """
    # 1. Handle Simple Scheme (No Filter)
    if col_filter is None:
        distributions: SimpleSchemeDict = {}
        
        # Get unique variables (e.g. Age, Gender)
        variables = df[col_variable].unique()
        
        for var in variables:
            # Filter for just this variable
            subset = df[df[col_variable] == var]
            
            # Create dict {Category: Value}
            # We use set_index + to_dict to map Category -> Value directly
            dist = subset.set_index(col_category)[col_value].to_dict()
            distributions[str(var)] = dist
            
        return distributions

    # 2. Handle Segmented Scheme (With Filter)
    else:
        segment_targets = {}
        segments = {}
        
        # Group by the segmentation column (e.g. Region)
        for seg_key, df_seg in df.groupby(col_filter, observed=True):
            seg_key_str = str(seg_key)
            
            # A. Calculate Global Target for this segment
            # Sum of ONE variable to get total pop (e.g. sum(Age) = Total Pop)
            # We pick the first variable found to calculate the total volume
            first_var = df_seg[col_variable].iloc[0]
            total_seg_weight = df_seg[df_seg[col_variable] == first_var][col_value].sum()
            segment_targets[seg_key_str] = total_seg_weight

            # B. Calculate Inner Targets
            inner_dists = {}
            variables = df_seg[col_variable].unique()
            
            for var in variables:
                subset = df_seg[df_seg[col_variable] == var]
                dist = subset.set_index(col_category)[col_value].to_dict()
                inner_dists[str(var)] = dist
            
            segments[seg_key_str] = inner_dists

        result: SegmentedSchemeDict = {
            "segment_by": col_filter,
            "segment_targets": segment_targets,
            "segments": segments
        }
        return result


def scheme_from_df(
    df: pd.DataFrame,
    cols_weighting: List[str],
    col_freq: str,
    col_filter: Optional[str] = None,
    name: Optional[str] = None,
    rim_params: Optional[Dict] = None
) -> Rim:
    """
    Extracts a weighting scheme from a reference microdata dataframe (row-per-record).

    This is useful when you have a representative dataset (e.g., Census microdata 
    or a high-quality random sample) where every row represents the combination of all demographic features, 
    and you want to calculate targets dynamically based on its distributions.

    Expected Input Format (Microdata):
    | Age   | Gender | Region | Weight/Freq |
    | 18-24 | Male   | East   | 1.0         |
    | 25-34 | Female | East   | 1.0         |
    | 65+   | Male   | West   | 2.5         |

    Args:
        df: The reference dataframe containing combinations of all demographic features.
        cols_weighting: List of columns to calculate targets for (e.g. ['Age', 'Gender']).
        col_freq: Column containing the weight or frequency of each row. 
                  (For raw census data, this is often a column of 1s).
        col_filter: Optional column for segmentation (e.g. 'Region').
                    If provided, targets are calculated within each unique value of this column.
        name: Name of the schema.
        rim_params: Parameters for the Rim class.

    Returns:
        Rim
    """
    scheme_definition = scheme_dict_from_df(
        df=df,
        cols_weighting=cols_weighting,
        col_freq=col_freq,
        col_filter=col_filter
    )
    return scheme_from_dict(
        distributions=scheme_definition,
        name=name,
        rim_params=rim_params
    )


def scheme_from_long_df(
    df: pd.DataFrame,
    col_variable: str,
    col_category: str,
    col_value: str,
    col_filter: Optional[str] = None,
    name: Optional[str] = None,
    rim_params: Optional[Dict] = None
) -> Rim:
    """
    Extracts a weighting scheme from a 'Long' or 'Tidy' aggregate dataframe.
    
    This is useful for census data where you have a table of totals rather 
    than individual rows.
    
    Expected Input Format:
    | Variable | Category | Value | (Optional Filter/Region) |
    | Age      | 18-24    | 500   | East                     |
    | Gender   | Male     | 480   | East                     |

    Args:
        df: The dataframe containing aggregate targets.
        col_variable: Column name identifying the dimension (e.g. 'Age', 'Gender')
        col_category: Column name identifying the group (e.g. '18-24', 'Male')
        col_value: Column name identifying the target weight/count.
        col_filter: Optional column for segmentation (e.g. 'Region')
        name: Name of the schema
        rim_params: Parameters for the Rim class

    Returns:
        Rim
    """
    scheme_definition = scheme_dict_from_long_df(
        df=df,
        col_variable=col_variable,
        col_category=col_category,
        col_value=col_value,
        col_filter=col_filter
    )
    return scheme_from_dict(
        distributions=scheme_definition,
        name=name,
        rim_params=rim_params
    )


def validate_scheme_dict(
    df: pd.DataFrame, 
    scheme: SchemeDict, 
    raise_error: bool = True
) -> Optional[pd.DataFrame]:
    """
    Validates a dataframe against a scheme dictionary.
    
    Checks if Data matches the Scheme (Columns, Categories, NaNs).

    Args:
        df: The survey dataframe to check.
        scheme: The dictionary defining the weighting scheme.
        raise_error: If True, raises a ValueError on the first Critical issue found.
                     If False, returns a DataFrame report of all issues.

    Returns:
        pd.DataFrame (if raise_error=False)
    """
    issues = []

    # --- Level 2: Validate Data Alignment (Post-normalization) ---
    
    # We convert to Rim object to reuse the robust matching logic (handling filters, types)
    # Note: scheme_from_dict WILL normalize the values here, so the Rim object 
    # is "clean", but we already caught the sum errors in Level 1.
    rim_object = scheme_from_dict(scheme, name="validation_temp")
    
    # Get data-level issues
    data_report = validate_scheme(df, rim_object, raise_error=False)
    
    # Combine reports
    if not data_report.empty:
        issues.extend(data_report.to_dict(orient='records'))
    
    report_df = pd.DataFrame(issues, columns=['group', 'variable', 'issue_type', 'severity', 'details'])

    if raise_error:
        errors = report_df[report_df['severity'] == 'Error']
        if not errors.empty:
            summary = "\n".join(
                f"[{row.group}] {row.variable} ({row.issue_type}): {row.details}" 
                for _, row in errors.iterrows()
            )
            raise ValueError(f"Validation Failed:\n{summary}")

    return report_df


def validate_scheme(
    df: pd.DataFrame, 
    scheme: Rim, 
    raise_error: bool = True
) -> Optional[pd.DataFrame]:
    """
    Validates a dataframe against a Rim scheme object.
    Checks for Columns, NaNs, and Category mismatches.
    """
    issues = []

    for group_name, group_def in scheme.groups.items():
        filter_def = group_def.get("filter_def")
        targets = group_def.get("targets", [])

        # 1. Apply Filter
        try:
            if filter_def:
                subset = df.query(filter_def)
            else:
                subset = df
        except Exception as e:
            issues.append({
                "group": group_name,
                "variable": "Filter",
                "issue_type": "Filter Error",
                "severity": "Error",
                "details": str(e)
            })
            continue

        if len(subset) == 0:
            issues.append({
                "group": group_name,
                "variable": "Filter",
                "issue_type": "Empty Group",
                "severity": "Warning",
                "details": f"Filter '{filter_def}' resulted in 0 rows."
            })
            continue

        # 2. Check Variables
        for target_wrapper in targets:
            var_name = list(target_wrapper.keys())[0]
            target_dist = target_wrapper[var_name]

            # Check Column Existence
            if var_name not in subset.columns:
                issues.append({
                    "group": group_name,
                    "variable": var_name,
                    "issue_type": "Missing Column",
                    "severity": "Error",
                    "details": f"Column '{var_name}' not found."
                })
                continue

            # Check NaNs
            nan_count = subset[var_name].isna().sum()
            if nan_count > 0:
                issues.append({
                    "group": group_name,
                    "variable": var_name,
                    "issue_type": "NaN Values",
                    "severity": "Error",
                    "details": f"Found {nan_count} NaNs."
                })

            # Check Category Mismatches
            # Normalize to strings for comparison
            target_keys = set(str(k) for k in target_dist.keys())
            data_keys = set(subset[var_name].dropna().astype(str).unique())

            # A. Missing in Data (Critical)
            # Categories present in Scheme but NOT in Data
            missing_in_data = target_keys - data_keys
            
            # Verify these aren't 0% targets (which are allowed to be missing)
            real_missing = []
            for k in missing_in_data:
                # Find original key
                orig_k = next(ok for ok in target_dist.keys() if str(ok) == k)
                if target_dist[orig_k] > 0:
                    real_missing.append(k)

            if real_missing:
                issues.append({
                    "group": group_name,
                    "variable": var_name,
                    "issue_type": "Missing in Data",
                    "severity": "Error",
                    "details": f"Categories in scheme but missing in data: {real_missing}"
                })

            # B. Missing in Scheme (Warning)
            # Categories present in Data but NOT in Scheme
            missing_in_scheme = data_keys - target_keys
            if missing_in_scheme:
                issues.append({
                    "group": group_name,
                    "variable": var_name,
                    "issue_type": "Missing in Scheme",
                    "severity": "Warning",
                    "details": f"Categories in data but missing in scheme: {list(missing_in_scheme)}"
                })

    report_df = pd.DataFrame(issues, columns=['group', 'variable', 'issue_type', 'severity', 'details'])

    if raise_error:
        errors = report_df[report_df['severity'] == 'Error']
        if not errors.empty:
            summary = "\n".join(
                f"[{row.group}] {row.variable}: {row.details}" 
                for _, row in errors.iterrows()
            )
            raise ValueError(f"Validation Failed:\n{summary}")

    return report_df