import pandas as pd

from weightipy.rim import Rim
from weightipy.version import version as __version__
from weightipy.weight_engine import WeightEngine


def weight_dataframe(df: pd.DataFrame, scheme: Rim, weight_column="weights") -> pd.DataFrame:
    df = df.copy()
    df["__identity__"] = range(len(df))
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
