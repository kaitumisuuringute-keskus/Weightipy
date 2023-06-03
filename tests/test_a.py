import unittest

import pandas as pd

from weightipy.rim import Rim
from weightipy import weight_dataframe, scheme_from_dict, weighting_efficiency, scheme_from_df

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