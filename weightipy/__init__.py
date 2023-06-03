import random
from typing import Dict, Union, Optional, List, Any

import pandas as pd

from weightipy.rim import Rim
from weightipy.version import version as __version__
from weightipy.weight_engine import WeightEngine


def weight_dataframe(df: pd.DataFrame, scheme: Rim, weight_column="weights") -> pd.DataFrame:
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
    engine.add_scheme(scheme=scheme, key="__identity__", verbose=False)
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


def schema_from_dict(
        distributions: Dict[str, Dict[Any, Union[float, int]]],
        name: Optional[str] = None,
        rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim schema from a dictionary of distributions. The dictionary should be in the format
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

def schema_from_df(
        df: pd.DataFrame,
        cols_weighting: List[str],
        col_freq: str,
        name: Optional[str] = None,
        rim_params: Optional[Dict] = None
) -> Rim:
    """
    Create a Rim schema from a dataframe.
    The dataframe should have columns for the dimensions to be weighted,
    and a column with the frequency of each row.

    This function is useful for simple schemas, where filters are not needed. For more complex schemas,
    use the Rim class directly.

    Args:
        df: Census dataframe
        cols_weighting: Columns to be weighted by
        col_freq: Column with the frequency of each row
        name: Name of the schema
        rim_params: Parameters for the Rim class

    Returns:

    """
    distributions = {}
    for col in cols_weighting:
        dist = df[[col, col_freq]].groupby(col).sum()[col_freq].to_dict()
        distributions[col] = dist

    return schema_from_dict(
        distributions=distributions,
        name=name,
        rim_params=rim_params
    )