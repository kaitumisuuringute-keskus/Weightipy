import unittest
import pandas as pd
import numpy as np
from weightipy import validate_scheme_dict

class TestValidation(unittest.TestCase):

    def setUp(self):
        # Standard Dataset
        self.df = pd.DataFrame({
            "gender": ["Male", "Female", "Male", "Female"],
            "age": ["18-24", "18-24", "25+", "25+"],
            "region": ["A", "A", "B", "B"]
        })

        # Standard Valid Scheme
        self.valid_scheme = {
            "gender": {"Male": 50.0, "Female": 50.0},
            "age": {"18-24": 50.0, "25+": 50.0}
        }

    def test_valid_match(self):
        """Happy Path: No errors."""
        report = validate_scheme_dict(self.df, self.valid_scheme, raise_error=False)
        self.assertTrue(report.empty)
        # Should not raise
        validate_scheme_dict(self.df, self.valid_scheme, raise_error=True)

    # --- Scenario: Value Only in Census (Missing in Data) ---

    def test_value_only_in_census(self):
        """
        Critical Error: Scheme has a target for a category that doesn't exist in the data.
        Infinite weights would occur.
        """
        # Scheme has "Non-binary", Data only has Male/Female
        scheme = {
            "gender": {"Male": 40.0, "Female": 40.0, "Non-binary": 20.0}
        }
        
        report = validate_scheme_dict(self.df, scheme, raise_error=False)
        
        err = report[report['issue_type'] == 'Missing in Data']
        self.assertFalse(err.empty, "Should report Missing in Data")
        self.assertEqual(err.iloc[0]['severity'], 'Error')
        self.assertIn("Non-binary", err.iloc[0]['details'])

    # --- Scenario: Value Only in Survey (Missing in Scheme) ---

    def test_value_only_in_survey(self):
        """
        Warning: Data has a category that is not in the scheme.
        Usually results in weight=1 or excluded rows.
        """
        # Data has "Male", Scheme only targets "Female" (100%)
        scheme = {
            "gender": {"Female": 100.0}
        }
        
        report = validate_scheme_dict(self.df, scheme, raise_error=False)
        
        warn = report[report['issue_type'] == 'Missing in Scheme']
        self.assertFalse(warn.empty, "Should report Missing in Scheme")
        self.assertEqual(warn.iloc[0]['severity'], 'Warning')
        self.assertIn("Male", warn.iloc[0]['details'])

    # --- Scenario: Zero-Target Exception ---

    def test_value_missing_in_data_but_zero_target(self):
        """
        Edge Case: Scheme has "Non-binary" but target is 0.0%.
        This should NOT be an error, even if missing in data.
        """
        scheme = {
            "gender": {"Male": 50.0, "Female": 50.0, "Non-binary": 0.0}
        }
        
        report = validate_scheme_dict(self.df, scheme, raise_error=False)
        self.assertTrue(report.empty, "0.0% targets should be ignored if missing in data")

    # --- Scenario: NaNs in Data ---

    def test_nan_error(self):
        """Error if weighting column has NaNs."""
        df_nan = self.df.copy()
        df_nan.loc[0, "gender"] = np.nan
        
        report = validate_scheme_dict(df_nan, self.valid_scheme, raise_error=False)
        
        err = report[report['issue_type'] == 'NaN Values']
        self.assertFalse(err.empty)
        self.assertEqual(err.iloc[0]['severity'], 'Error')

    # --- Scenario: Nested/Segmented Mismatch ---

    def test_segmented_errors(self):
        """Test validation inside segments."""
        nested_scheme = {
            "segment_by": "region",
            "segment_targets": {"A": 50.0, "B": 50.0},
            "segments": {
                "A": {"gender": {"Male": 100.0}}, # A: Warning (Female in data, not scheme)
                "B": {"gender": {"Alien": 100.0}} # B: Error (Alien in scheme, not data)
            }
        }
        
        report = validate_scheme_dict(self.df, nested_scheme, raise_error=False)
        
        # Check Region A
        err_a = report[(report['group'] == 'A') & (report['variable'] == 'gender')]
        self.assertEqual(err_a.iloc[0]['issue_type'], 'Missing in Scheme')
        
        # Check Region B
        err_b = report[(report['group'] == 'B') & (report['variable'] == 'gender')]
        self.assertEqual(err_b.iloc[0]['issue_type'], 'Missing in Data')
        self.assertIn("Alien", err_b.iloc[0]['details'])

if __name__ == '__main__':
    unittest.main()