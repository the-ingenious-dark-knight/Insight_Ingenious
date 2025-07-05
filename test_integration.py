#!/usr/bin/env python3
"""
Integration test to verify both hyphenated and underscored workflow names work correctly.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ingenious.utils.namespace_utils import normalize_workflow_name


def test_workflow_module_path_generation():
    """Test that workflow module paths are generated correctly with normalization."""

    # Test cases: (input_workflow_name, expected_module_path)
    test_cases = [
        (
            "bike-insights",
            "services.chat_services.multi_agent.conversation_flows.bike_insights.bike_insights",
        ),
        (
            "bike_insights",
            "services.chat_services.multi_agent.conversation_flows.bike_insights.bike_insights",
        ),
        (
            "classification-agent",
            "services.chat_services.multi_agent.conversation_flows.classification_agent.classification_agent",
        ),
        (
            "classification_agent",
            "services.chat_services.multi_agent.conversation_flows.classification_agent.classification_agent",
        ),
    ]

    print("Testing workflow module path generation:")
    print("=" * 70)

    all_passed = True
    for input_name, expected_path in test_cases:
        # Simulate the logic from the multi_agent service
        normalized_flow = normalize_workflow_name(input_name)
        actual_path = f"services.chat_services.multi_agent.conversation_flows.{normalized_flow}.{normalized_flow}"

        passed = actual_path == expected_path
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} | '{input_name}' -> '{actual_path}'")
        if not passed:
            print(f"      Expected: '{expected_path}'")
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("🎉 All workflow path generation tests passed!")
        return True
    else:
        print("❌ Some workflow path generation tests failed!")
        return False


def test_api_diagnostic_normalization():
    """Test that the API diagnostic route normalizes workflow names correctly."""

    # Import the function we updated
    from ingenious.api.routes.diagnostic import normalize_workflow_name

    # Test cases that would be used in API calls
    test_cases = [
        ("bike-insights", "bike_insights"),
        ("classification-agent", "classification_agent"),
        ("knowledge-base-agent", "knowledge_base_agent"),
        ("sql-manipulation-agent", "sql_manipulation_agent"),
    ]

    print("\nTesting API diagnostic normalization:")
    print("=" * 50)

    all_passed = True
    for api_input, expected_lookup in test_cases:
        normalized = normalize_workflow_name(api_input)
        passed = normalized == expected_lookup
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} | API: '{api_input}' -> Lookup: '{normalized}'")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 All API diagnostic tests passed!")
        return True
    else:
        print("❌ Some API diagnostic tests failed!")
        return False


if __name__ == "__main__":
    success1 = test_workflow_module_path_generation()
    success2 = test_api_diagnostic_normalization()

    overall_success = success1 and success2

    print("\n" + "=" * 70)
    if overall_success:
        print(
            "🚀 All integration tests passed! Both hyphenated and underscored workflow names are supported."
        )
        print("\nNow users can use either format:")
        print('• "conversation_flow": "bike-insights"   (preferred)')
        print('• "conversation_flow": "bike_insights"   (legacy, still works)')
    else:
        print("❌ Some integration tests failed!")

    sys.exit(0 if overall_success else 1)
