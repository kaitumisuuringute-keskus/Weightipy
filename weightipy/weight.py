import random
from numbers import Number
from typing import Dict, Mapping, TypedDict, Union, Optional, List, Any, cast

import pandas as pd

from weightipy.internal.rim import Rim
from weightipy.version import version as __version__
from weightipy.internal.weight_engine import WeightEngine



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

