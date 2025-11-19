import unittest
import pandas as pd
from weightipy import scheme_from_long_df, scheme_dict_from_long_df

class TestLongFormat(unittest.TestCase):

    def setUp(self):
        """
        Setup common data for both tests.
        Format: | Region | Variable | Category | Count |
        """
        data = {
            "Region": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "Variable": ["Gender", "Gender", "Age", "Age", "Gender", "Gender", "Age", "Age"],
            "Category": ["Male", "Female", "Young", "Old", "Male", "Female", "Young", "Old"],
            "Count": [
                40, 60,  # Region A Gender (Total 100)
                30, 70,  # Region A Age (Total 100)
                50, 50,  # Region B Gender (Total 100)
                20, 80   # Region B Age (Total 100)
            ]
        }
        self.df_targets = pd.DataFrame(data)

    def test_dict_extraction_from_long_df(self):
        """
        STEP 1: Verify the intermediate dictionary is created correctly.
        We expect RAW counts here (e.g., 100), not percentages. 
        Normalization happens later in scheme_from_dict.
        """
        result = scheme_dict_from_long_df(
            df=self.df_targets,
            col_variable="Variable",
            col_category="Category",
            col_value="Count",
            col_filter="Region"
        )

        # 1. Check Structure
        self.assertEqual(result["segment_by"], "Region")
        
        # 2. Check Segment Targets (Total Volume calculation)
        # It should sum ONE variable (e.g. Gender) to get the total population for the region.
        # Region A total = 40 (Male) + 60 (Female) = 100
        self.assertEqual(result["segment_targets"]["A"], 100)
        self.assertEqual(result["segment_targets"]["B"], 100)

        # 3. Check Inner Distributions (Raw Counts)
        # Region A -> Gender -> Male should be 40
        self.assertEqual(result["segments"]["A"]["Gender"]["Male"], 40)
        self.assertEqual(result["segments"]["A"]["Gender"]["Female"], 60)
        
        # Region B -> Age -> Old should be 80
        self.assertEqual(result["segments"]["B"]["Age"]["Old"], 80)

    def test_scheme_object_creation(self):
        """
        STEP 2: Verify the dictionary is successfully converted to a Rim object.
        """
        scheme = scheme_from_long_df(
            df=self.df_targets,
            col_variable="Variable",
            col_category="Category",
            col_value="Count",
            col_filter="Region",
            name="test_scheme"
        )

        # Verify the object was created and has the correct groups
        self.assertIn("A", scheme.groups)
        self.assertIn("B", scheme.groups)

        # To verify the percentages, we inspect the internal targets of group 'A'
        # We know A had 40 Male / 60 Female.
        # The Rim object should have normalized this to 40.0% and 60.0%
        
        group_a_targets = scheme.groups["A"]["targets"]
        
        # Helper to find 'Gender' in the list of targets [{"Gender": ...}, {"Age": ...}]
        gender_dist = next(t["Gender"] for t in group_a_targets if "Gender" in t)
        
        self.assertEqual(gender_dist["Male"], 40.0)
        self.assertEqual(gender_dist["Female"], 60.0)