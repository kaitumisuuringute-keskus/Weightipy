import random
from numbers import Number
from typing import Dict, Union, Optional, List, Any

import pandas as pd

from weightipy.rim import Rim
from weightipy.version import version as __version__
from weightipy.weight_engine import WeightEngine


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


def weighting_efficiency(weights: pd.Series) -> float:
    sws = (weights.sum()) ** 2
    ssw = (weights ** 2).sum()
    return (sws / len(weights)) / ssw * 100


def scheme_from_dict(
        distributions: Dict[str, Dict[Any, Union[float, int]]],
        name: Optional[str] = None,
        rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim scheme from a dictionary of distributions. The dictionary should be in the format
    {dimension: {value: proportion}}. The proportions should be in percentages, e.g. 0.5 for 50%.

    This function is useful for simple schemas, where filters are not needed. For more complex schemas,
    use the Rim class directly.

    Args:
        distributions: Dictionary of distributions
        name: Name of the schema
        rim_params: Parameters for the Rim class

    Returns:

    """
    if rim_params is None:
        rim_params = {}
    if name is None:
        # add random name
        name = "generated" + str(random.randint(0, 1000000))

    # normalize distributions to 100
    for dim, dist in distributions.items():
        total = sum(dist.values())
        for k, v in dist.items():
            dist[k] = v / total * 100

    global_targets = []
    for dim, dist in distributions.items():
        global_targets.append({dim: dist})

    schema = Rim(name, **rim_params)
    schema.set_targets(
        targets=global_targets, group_name="global group"
    )
    return schema

def scheme_from_df(
        df: pd.DataFrame,
        cols_weighting: List[str],
        col_freq: str,
        col_filter: Optional[str] = None,
        name: Optional[str] = None,
        rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim scheme from a dataframe.
    The dataframe should have columns for the dimensions to be weighted,
    and a column with the frequency of each row.

    This function supports complex schemas where groups need
    to be defined by a single filter column (group per unique value, excluding nans).
    Simplest use case is to use a region column to define groups. The distribution
    of groups between each other is also used as a target.

    Args:
        df: Census dataframe
        cols_weighting: Columns to be weighted by
        col_freq: Column with the frequency of each row
        col_filter: Column to be used as a filter. Unique values in this column will be used to define groups, each weighted separetly.
        name: Name of the schema
        rim_params: Parameters for the Rim class

    Returns:

    """
    if name is None:
        name = "generated" + str(random.randint(0, 1000000))
    if rim_params is None:
        rim_params = {}

    if col_filter is None:
        distributions = {}
        for col in cols_weighting:
            dist = df[[col, col_freq]].groupby(col).sum()[col_freq].to_dict()
            distributions[col] = dist

        return scheme_from_dict(
            distributions=distributions,
            name=name,
            rim_params=rim_params
        )
    else:
        scheme = Rim(name, **rim_params)
        total = df[col_freq].sum()
        group_targets = {}

        for u in df[col_filter].unique():
            if pd.isna(u):
                continue
            # Get target distributions
            df_filter = df[df[col_filter] == u]
            filter_total = df_filter[col_freq].sum()

            targets = {}

            for wcol in cols_weighting:
                dist = df_filter[[wcol, col_freq]].groupby(wcol).sum()[col_freq] / filter_total * 100
                dist = dist.to_dict()

                targets[wcol] = dist

            # use pandas query to define filter
            if isinstance(u, str):
                filter_def = f"`{col_filter}` == '{u}'"
            elif isinstance(u, Number):
                filter_def = f"`{col_filter}` == {u}"
            else:
                raise ValueError(f"Unknown type for filter value: {type(u)}")

            group_name = f"{col_filter}={u}"
            scheme.add_group(
                name=group_name,
                filter_def=filter_def,
                targets=targets
            )
            group_targets[group_name] = filter_total / total * 100

        scheme.group_targets(group_targets)

        return scheme