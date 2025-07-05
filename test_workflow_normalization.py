#!/usr/bin/env python3
"""
Test script to verify workflow name normalization works correctly.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ingenious.utils.namespace_utils import normalize_workflow_name


def test_normalize_workflow_name():
    """Test the normalize_workflow_name function."""

    # Test cases: (input, expected_output)
    test_cases = [
        ("bike-insights", "bike_insights"),
        ("bike_insights", "bike_insights"),
        ("classification-agent", "classification_agent"),
        ("classification_agent", "classification_agent"),
        ("knowledge-base-agent", "knowledge_base_agent"),
        ("knowledge_base_agent", "knowledge_base_agent"),
        ("sql-manipulation-agent", "sql_manipulation_agent"),
        ("sql_manipulation_agent", "sql_manipulation_agent"),
        ("BIKE-INSIGHTS", "bike_insights"),  # Test uppercase
        ("", ""),  # Test empty string
        ("single", "single"),  # Test single word
        ("multi-word-workflow", "multi_word_workflow"),  # Test multiple hyphens
    ]

    print("Testing normalize_workflow_name function:")
    print("=" * 50)

    all_passed = True
    for input_name, expected_output in test_cases:
        actual_output = normalize_workflow_name(input_name)
        passed = actual_output == expected_output
        status = "✅ PASS" if passed else "❌ FAIL"

        print(
            f"{status} | Input: '{input_name}' -> Output: '{actual_output}' (Expected: '{expected_output}')"
        )

        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = test_normalize_workflow_name()
    sys.exit(0 if success else 1)
