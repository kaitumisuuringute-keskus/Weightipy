
import random
from typing import Dict, List, Optional, cast

import pandas as pd
from weightipy.internal.helpers import _is_numeric_str, _normalize_simple_dict
from weightipy.internal.rim import Rim
from weightipy.types import SchemeDict, SegmentedSchemeDict, SimpleSchemeDict


def scheme_from_dict(
    distributions: SchemeDict,
    name: Optional[str] = None,
    rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim scheme from a dictionary.
    
    Supports two formats:
    
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

    Parameters
    ----------
    distributions : SchemeDict
        Dictionary definition of the scheme
    name : str, optional
        Name of the schema
    rim_params : dict, optional
        Parameters for the Rim class

    Returns
    -------
    Rim
        A configured Rim object
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
    Extract a weighting scheme dict from a reference microdata dataframe.

    This is useful when you have a representative dataset (e.g., Census microdata
    or a high-quality random sample) where every row represents the combination of all demographic features,
    and you want to calculate targets dynamically based on its distributions.

    Expected Input Format (Microdata):
    | Age   | Gender | Region | Weight/Freq |
    | 18-24 | Male   | East   | 1.0         |
    | 25-34 | Female | East   | 1.0         |
    | 65+   | Male   | West   | 2.5         |

    Parameters
    ----------
    df : pd.DataFrame
        The reference dataframe containing combinations of all demographic features
    cols_weighting : list of str
        List of columns to calculate targets for (e.g. ['Age', 'Gender'])
    col_freq : str
        Column containing the weight or frequency of each row.
        (For raw census data, this is often a column of 1s)
    col_filter : str, optional
        Optional column for segmentation (e.g. 'Region').
        If provided, targets are calculated within each unique value of this column

    Returns
    -------
    SchemeDict
        Dictionary containing the weighting scheme
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
    Extract a weighting scheme dict from a 'Long' or 'Tidy' aggregate dataframe.
    
    This is useful for census data where you have a table of totals rather
    than individual rows.
    
    Expected Input Format:
    | Variable | Category | Value | (Optional Filter/Region) |
    | Age      | 18-24    | 500   | East                     |
    | Gender   | Male     | 480   | East                     |

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing aggregate targets
    col_variable : str
        Column name identifying the dimension (e.g. 'Age', 'Gender')
    col_category : str
        Column name identifying the group (e.g. '18-24', 'Male')
    col_value : str
        Column name identifying the target weight/count
    col_filter : str, optional
        Optional column for segmentation (e.g. 'Region')

    Returns
    -------
    SchemeDict
        Dictionary containing the weighting scheme
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
    Extract a weighting scheme from a reference microdata dataframe.

    This is useful when you have a representative dataset (e.g., Census microdata
    or a high-quality random sample) where every row represents the combination of all demographic features,
    and you want to calculate targets dynamically based on its distributions.

    Expected Input Format (Microdata):
    | Age   | Gender | Region | Weight/Freq |
    | 18-24 | Male   | East   | 1.0         |
    | 25-34 | Female | East   | 1.0         |
    | 65+   | Male   | West   | 2.5         |

    Parameters
    ----------
    df : pd.DataFrame
        The reference dataframe containing combinations of all demographic features
    cols_weighting : list of str
        List of columns to calculate targets for (e.g. ['Age', 'Gender'])
    col_freq : str
        Column containing the weight or frequency of each row.
        (For raw census data, this is often a column of 1s)
    col_filter : str, optional
        Optional column for segmentation (e.g. 'Region').
        If provided, targets are calculated within each unique value of this column
    name : str, optional
        Name of the schema
    rim_params : dict, optional
        Parameters for the Rim class

    Returns
    -------
    Rim
        A configured Rim object
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
    Extract a weighting scheme from a 'Long' or 'Tidy' aggregate dataframe.
    
    This is useful for census data where you have a table of totals rather
    than individual rows.
    
    Expected Input Format:
    | Variable | Category | Value | (Optional Filter/Region) |
    | Age      | 18-24    | 500   | East                     |
    | Gender   | Male     | 480   | East                     |

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing aggregate targets
    col_variable : str
        Column name identifying the dimension (e.g. 'Age', 'Gender')
    col_category : str
        Column name identifying the group (e.g. '18-24', 'Male')
    col_value : str
        Column name identifying the target weight/count
    col_filter : str, optional
        Optional column for segmentation (e.g. 'Region')
    name : str, optional
        Name of the schema
    rim_params : dict, optional
        Parameters for the Rim class

    Returns
    -------
    Rim
        A configured Rim object
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

