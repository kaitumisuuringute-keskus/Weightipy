
"""
Validation utilities for weighting schemes.

This module provides functions to validate survey dataframes against weighting
schemes before applying weights. Validation checks include column existence,
missing values, and category mismatches between the data and scheme definitions.
"""

from typing import Optional
import pandas as pd

from weightipy.internal.rim import Rim
from weightipy.scheme import scheme_from_dict
from weightipy.types import SchemeDict


def validate_scheme_dict(
    df: pd.DataFrame,
    scheme: SchemeDict,
    raise_error: bool = True
) -> Optional[pd.DataFrame]:
    """
    Validate a dataframe against a scheme dictionary.
    
    Checks if Data matches the Scheme (Columns, Categories, NaNs).

    Parameters
    ----------
    df : pd.DataFrame
        The survey dataframe to check
    scheme : SchemeDict
        The dictionary defining the weighting scheme
    raise_error : bool, default True
        If True, raises a ValueError on the first Critical issue found.
        If False, returns a DataFrame report of all issues

    Returns
    -------
    pd.DataFrame or None
        DataFrame report of all issues if raise_error=False, None otherwise
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
    if data_report is not None and not data_report.empty:
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
    Validate a dataframe against a Rim scheme object.
    
    Checks for Columns, NaNs, and Category mismatches.

    Parameters
    ----------
    df : pd.DataFrame
        The survey dataframe to check
    scheme : Rim
        The Rim scheme object defining the weighting scheme
    raise_error : bool, default True
        If True, raises a ValueError on the first Critical issue found.
        If False, returns a DataFrame report of all issues

    Returns
    -------
    pd.DataFrame or None
        DataFrame report of all issues if raise_error=False, None otherwise
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