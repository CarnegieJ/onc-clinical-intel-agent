"""
MODULE: Clinical Safety Guardrails
COPYRIGHT: © 2025 [Carnegie Johnson/IAYF Consulting]. All Rights Reserved.
DESCRIPTION: Middleware to detect/redact PII and enforce safety policies.
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv, find_dotenv

# Import isolated configuration
try:
    from .pii_patterns import PATTERNS
except ImportError:
    # Handle running script directly vs as module
    from pii_patterns import PATTERNS

# Try to import Azure libraries
try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(), override=True)

class ClinicalGuardrails:
    def __init__(self, use_simulation: bool = True, keywords_file: str = "unsafe_keywords.txt") -> None:
        self.use_simulation = use_simulation
        self.pii_patterns = PATTERNS
        self.unsafe_keywords = self._load_keywords(keywords_file)
        
        # Setup Azure Client
        if not self.use_simulation:
            if not AZURE_AVAILABLE:
                logger.warning("Library 'azure-ai-contentsafety' missing. Reverting to Sim Mode.")
                self.use_simulation = True
                return

            endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
            key = os.getenv("AZURE_CONTENT_SAFETY_KEY")
            
            if endpoint and key:
                self.client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
            else:
                self.use_simulation = True

    def _load_keywords(self, filename: str) -> List[str]:
        """Loads simulation keywords from a text file relative to this script."""
        keywords = []
        try:
            # Resolve path relative to this script file
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, filename)
            
            with open(full_path, 'r') as f:
                keywords = [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            logger.warning(f"Warning: '{filename}' not found. Using default unsafe list.")
            keywords = ["kill", "harm", "hack"]
        return keywords

    def scan_for_pii(self, text: str) -> dict:
        """Regex-based PII Scrubber"""
        detected = {}
        safe_text = text

        for label, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[label] = matches
                for match in matches:
                    safe_text = safe_text.replace(match, f"[{label}_REDACTED]")

        return {
            "has_pii": len(detected) > 0,
            "detected_entities": detected,
            "sanitized_text": safe_text
        }

    def check_content_safety(self, text: str) -> Dict[str, Any]:
        if self.use_simulation:
            return self._simulate_safety_check(text)
        else:
            return self._call_azure_safety_api(text)

    def _simulate_safety_check(self, text: str) -> Dict[str, Any]:
        """Checks against loaded keyword list"""
        text_lower = text.lower()
        for word in self.unsafe_keywords:
            if word in text_lower:
                return {"safe": False, "category": "Violence/Harm (Simulated)", "confidence": 0.95}
        return {"safe": True, "category": "None", "confidence": 0.0}

    def _call_azure_safety_api(self, text: str) -> Dict[str, Any]:
        """Real Azure AI Content Safety Call"""
        try:
            request = AnalyzeTextOptions(text=text)
            response = self.client.analyze_text(request)
            
            for category in response.categories_analysis:
                if category.severity >= 2: 
                    return {
                        "safe": False,
                        "category": category.category,
                        "confidence": category.severity / 4.0
                    }
            return {"safe": True, "category": "None", "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"Azure API Error: {e}")
            return {"safe": False, "category": "API_ERROR", "confidence": 1.0}

    def validate_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Master Validation Pipeline"""
        # 1. PII Check
        pii = self.scan_for_pii(user_prompt)
        if pii["has_pii"]:
            return {"allowed": False, "reason": "PII Detected", "details": pii}

        # 2. Content Safety
        safety = self.check_content_safety(user_prompt)
        if not safety["safe"]:
            return {"allowed": False, "reason": "Content Violation", "details": safety}

        return {"allowed": True, "clean_prompt": user_prompt}