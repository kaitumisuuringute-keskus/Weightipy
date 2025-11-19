import unittest
import pandas as pd
import numpy as np
from weightipy import (
    weight_dataframe, 
    scheme_from_dict, 
    scheme_from_df, 
    scheme_dict_from_df
)

class TestNestedSchemes(unittest.TestCase):

    def setUp(self):
        # Create a synthetic dataset
        # Region A: Skewed Male
        # Region B: Skewed Female
        data = {
            "region": ["A"] * 50 + ["B"] * 50,
            "gender": ["Male"] * 40 + ["Female"] * 10 + ["Male"] * 10 + ["Female"] * 40,
            "age_group": ["18-24"] * 25 + ["25+"] * 25 + ["18-24"] * 25 + ["25+"] * 25,
            "weight_col": [1] * 100
        }
        self.df = pd.DataFrame(data)

    def test_scheme_dict_from_df_structure(self):
        """
        Test if scheme_dict_from_df correctly extracts a SegmentedSchemeDict structure.
        """
        # Extract scheme dict
        scheme_dict = scheme_dict_from_df(
            self.df,
            cols_weighting=["gender"],
            col_freq="weight_col",
            col_filter="region"
        )

        # Check top level keys
        self.assertIn("segment_by", scheme_dict)
        self.assertEqual(scheme_dict["segment_by"], "region")
        
        # Check segment targets (total counts per region)
        # We have 50 rows in A and 50 in B, weight 1 each
        self.assertEqual(scheme_dict["segment_targets"]["A"], 50)
        self.assertEqual(scheme_dict["segment_targets"]["B"], 50)

        # Check inner segments
        self.assertIn("A", scheme_dict["segments"])
        self.assertIn("B", scheme_dict["segments"])
        
        # Check inner distribution counts (Region A has 40 Males)
        self.assertEqual(scheme_dict["segments"]["A"]["gender"]["Male"], 40)
        self.assertEqual(scheme_dict["segments"]["A"]["gender"]["Female"], 10)

    def test_manual_nested_scheme_integration(self):
        """
        Test creating a nested scheme manually and applying it.
        We will try to force Region A to be 50/50 gender (currently 80/20).
        """
        distributions = {
            "segment_by": "region",
            "segment_targets": {"A": 50.0, "B": 50.0}, # Equal population size
            "segments": {
                "A": {
                    "gender": {"Male": 50.0, "Female": 50.0} # Force to 50/50
                },
                "B": {
                    "gender": {"Male": 20.0, "Female": 80.0} # Keep as is (approx)
                }
            }
        }

        # Create scheme
        scheme = scheme_from_dict(distributions)
        
        # Weight dataframe
        df_weighted = weight_dataframe(self.df, scheme, weight_column="w_new")

        # Verify Region A results
        df_a = df_weighted[df_weighted["region"] == "A"]
        total_weight_a = df_a["w_new"].sum()
        male_weight_a = df_a[df_a["gender"] == "Male"]["w_new"].sum()
        
        # Should be close to 50%
        self.assertAlmostEqual(male_weight_a / total_weight_a, 0.5, places=2)

        # Verify Global proportions (A vs B should be 50/50)
        total_weight = df_weighted["w_new"].sum()
        self.assertAlmostEqual(total_weight_a / total_weight, 0.5, places=2)

    def test_auto_nested_scheme_from_reference(self):
        """
        Test the full pipeline: scheme_from_df (with filter) -> weight_dataframe.
        We use the self.df as the 'census' target, and weight a biased sample to match it.
        """
        # Create a biased sample (Sample has very few people in Region A)
        sample_data = {
            "region": ["A"] * 10 + ["B"] * 90,
            "gender": ["Male"] * 5 + ["Female"] * 5 + ["Male"] * 45 + ["Female"] * 45,
            "w": [1] * 100
        }
        df_sample = pd.DataFrame(sample_data)

        # Generate scheme from the balanced 'census' (self.df)
        # self.df has 50/50 region split. Sample has 10/90.
        schema = scheme_from_df(
            self.df,
            cols_weighting=["gender"],
            col_freq="weight_col",
            col_filter="region"
        )

        # Weight the sample
        df_weighted = weight_dataframe(df_sample, schema, weight_column="weights")

        # Check if the weighted sample matches the census region distribution (50/50)
        grouped = df_weighted.groupby("region")["weights"].sum()
        total = grouped.sum()
        
        # Both regions should now represent ~50% of the total weight, 
        # even though Region A was only 10% of the sample rows.
        self.assertAlmostEqual(grouped["A"] / total, 0.50, delta=0.05)

    def test_numeric_segmentation_column(self):
        """
        Test edge case where the segmentation column is integers, not strings.
        This verifies the `_is_numeric_str` or filter generation logic.
        """
        # Create data with numeric regions [1, 2]
        df_num = self.df.copy()
        df_num["region_id"] = df_num["region"].map({"A": 1, "B": 2})
        
        # Create target scheme dict manually using string keys (since JSON keys are strings)
        distributions = {
            "segment_by": "region_id",
            "segment_targets": {"1": 50.0, "2": 50.0},
            "segments": {
                "1": {"gender": {"Male": 50.0, "Female": 50.0}},
                "2": {"gender": {"Male": 50.0, "Female": 50.0}}
            }
        }

        scheme = scheme_from_dict(distributions, name="numeric_test")
        
        # This should not raise a syntax error during pandas query
        # It relies on `region_id` == '1' working in pandas query engine 
        # or the internal conversion handling it.
        df_weighted = weight_dataframe(df_num, scheme)
        
        # Verify it actually worked (weights are not all 1 or NaN)
        self.assertFalse(df_weighted["weights"].isna().any())
        self.assertNotEqual(df_weighted["weights"].std(), 0.0)

if __name__ == '__main__':
    unittest.main()