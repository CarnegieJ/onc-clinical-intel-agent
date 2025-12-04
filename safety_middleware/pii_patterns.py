"""
CONFIG: PII Regex Patterns
Description: Central repository for Regular Expressions used to identify sensitive entities.
"""

PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "PHONE": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
    # Custom Pattern for Oncology Data (e.g., TCGA-OR-A5J1)
    "PATIENT_ID": r'\bTCGA-[A-Z0-9]{2}-[A-Z0-9]{4}\b' 
}