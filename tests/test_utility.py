import unittest

import numpy as np
import pandas as pd

from weightipy.rim import Rim
from weightipy import scheme_from_long_df, weight_dataframe, scheme_from_dict, weighting_efficiency, scheme_from_df

class TestUtility(unittest.TestCase):

    def test_schema_from_distribution(self):
        df = pd.read_csv("./tests/Example Data (A).csv")
        dist = {
            "gender": {
                1: 0.5,
                2: 0.5
            }
        }
        schema = scheme_from_dict(dist)
        df = weight_dataframe(df, schema)
        eff = weighting_efficiency(df["weights"])
        self.assertGreater(eff, 10)
        self.assertLess(eff, 100)

    def test_schema_from_df(self):
        df = pd.read_csv("./tests/Example Data (A).csv")
        df["n"] = 1
        schema = scheme_from_df(df, cols_weighting=["gender", "age"], col_freq="n")
        df = weight_dataframe(df, schema)
        eff = weighting_efficiency(df["weights"])
        self.assertLess(abs(eff - 100.0), 1.0)

    def test_complex_schema_from_df(self):
        df = pd.read_csv("./tests/Example Data (A).csv")
        df["n"] = (np.random.random(len(df)) - 0.5) / 1.0 + 1.0
        df["gender"] = df["gender"].astype(str)
        schema = scheme_from_df(
            df,
            cols_weighting=["age"],
            col_filter="gender",
            col_freq="n"
        )
        df = weight_dataframe(df, schema, verbose=True)
        eff = weighting_efficiency(df["weights"])
        self.assertNotEqual(eff, 100.0)
        self.assertGreater(eff, 95.0)
        self.assertTrue(df["weights"].isna().mean() == 0.0)
