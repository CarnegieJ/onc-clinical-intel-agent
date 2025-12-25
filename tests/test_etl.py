"""
Unit tests for ETL logic and data validation.
"""

import unittest
import os
import tempfile
import pandas as pd
from safety_middleware.pii_patterns import PATTERNS


class TestETL(unittest.TestCase):
    def test_pii_patterns_loaded(self):
        """Test that PII patterns are loaded correctly."""
        self.assertIn("EMAIL", PATTERNS)
        self.assertIn("PATIENT_ID", PATTERNS)

    def test_sample_data_loading(self):
        """Test loading sample clinical data."""
        # Create a temporary CSV file
        sample_data = """PATIENT_ID\tAGE\tSURVIVAL_MONTHS
TCGA-01-0001\t50\t24
TCGA-02-0002\t60\t36
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_data)
            temp_file = f.name

        try:
            # Load with pandas like in ETL
            df = pd.read_csv(temp_file, sep='\t', comment='#')
            self.assertEqual(len(df), 2)
            self.assertIn('PATIENT_ID', df.columns)
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
