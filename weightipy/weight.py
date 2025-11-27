"""
Core weighting functions.

This module provides the main functions for applying weights to survey data
using the RIM (Raking) algorithm. It includes functions to weight dataframes,
return weight series, and calculate weighting efficiency metrics.
"""

import random
from numbers import Number
from typing import Dict, Mapping, TypedDict, Union, Optional, List, Any, cast

import pandas as pd

from weightipy.internal.rim import Rim
from weightipy.version import version as __version__
from weightipy.internal.weight_engine import WeightEngine

def weight(df: pd.DataFrame, scheme: Rim, verbose=False) -> pd.Series:
    """
    Weight a dataframe using a Rim scheme.
    
    The dataframe must have a column for each dimension in the scheme.
    String columns are automatically converted to categorical, allowing easier processing.

    Parameters
    ----------
    df : pd.DataFrame
        The survey dataframe to weight
    scheme : Rim
        The Rim scheme object defining the weighting targets
    verbose : bool, default False
        If True, prints progress information

    Returns
    -------
    pd.Series
        A series containing the calculated weights
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
    Weight a dataframe using a Rim scheme and return the weighted dataframe.
    
    The dataframe must have a column for each dimension in the scheme.
    String columns are automatically converted to categorical, allowing easier processing.

    Parameters
    ----------
    df : pd.DataFrame
        The survey dataframe to weight
    scheme : Rim
        The Rim scheme object defining the weighting targets
    weight_column : str, default "weights"
        Name of the column to store the calculated weights
    verbose : bool, default False
        If True, prints progress information

    Returns
    -------
    pd.DataFrame
        The input dataframe with an additional weight column
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
    """
    Calculate the weighting efficiency (Kish's effective sample size).
    
    This metric indicates how much the sample size is reduced due to weighting.
    Higher values (closer to 100%) indicate more efficient weights.

    Parameters
    ----------
    weights : pd.Series
        Series containing the calculated weights

    Returns
    -------
    float
        The weighting efficiency as a percentage (0-100)
    """
    sws = (weights.sum()) ** 2
    ssw = (weights ** 2).sum()
    return (sws / len(weights)) / ssw * 100

