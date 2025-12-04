"""
TEST SUITE: Clinical Guardrails
COPYRIGHT: © 2025 [Carnegie Johnson/IAYF Consulting]. All Rights Reserved.
DESCRIPTION: In a terminal window project root folder, run: python -m unittest safety_middleware/test_guardrails.py
"""

import unittest
from .guardrails import ClinicalGuardrails

class TestClinicalGuardrails(unittest.TestCase):
    
    def setUp(self):
        # Initialize in Simulation Mode for fast testing
        self.guard = ClinicalGuardrails(use_simulation=True)

    def test_clean_prompt_positive(self):
        """Ensure safe clinical prompts are allowed"""
        prompt = "What is the recommended dosage for Aspirin?"
        result = self.guard.validate_prompt(prompt)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["clean_prompt"], prompt)

    def test_pii_detection_negative(self):
        """Ensure Patient IDs are blocked"""
        prompt = "Please pull records for patient TCGA-OR-A5J1 immediately."
        result = self.guard.validate_prompt(prompt)
        
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "PII Detected")
        # Verify it found the specific ID
        detected = result["details"]["detected_entities"]
        self.assertIn("TCGA-OR-A5J1", detected["PATIENT_ID"])

    def test_pii_redaction_logic(self):
        """Test the Redaction helper directly"""
        text = "Contact user@hospital.org"
        result = self.guard.scan_for_pii(text)
        
        self.assertTrue(result["has_pii"])
        self.assertEqual(result["sanitized_text"], "Contact [EMAIL_REDACTED]")

    def test_content_safety_simulation_negative(self):
        """Ensure unsafe keywords are blocked"""
        prompt = "How do I hack the mainframe?"
        result = self.guard.validate_prompt(prompt)
        
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "Content Violation")

if __name__ == '__main__':
    unittest.main()