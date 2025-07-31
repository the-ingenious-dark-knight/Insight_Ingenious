#!/usr/bin/env python3
"""
Upload bike-insights template files to Azure Blob Storage via Ingenious API

This script solves the common issue where bike-insights workflow fails with
"The specified blob does not exist" error due to missing prompt templates.

Usage:
    python scripts/upload_bike_templates.py

Prerequisites:
    - Ingenious server running with Azure Blob Storage configured
    - Local template files available in ingenious_extensions_template/templates/prompts/
"""

from pathlib import Path

import requests

# Configuration
API_BASE = "http://localhost:8000"
REVISION_ID = "test-v1"

# Templates needed for bike-insights workflow
TEMPLATE_FILES = [
    "customer_sentiment_agent_prompt.jinja",
    "fiscal_analysis_agent_prompt.jinja",
    "summary_prompt.jinja",
    "bike_lookup_agent_prompt.jinja",
    "user_proxy_prompt.jinja",
]


def read_local_template(filename: str) -> str | None:
    """Read template content from local installation"""
    template_path = (
        Path("ingenious/ingenious_extensions_template/templates/prompts") / filename
    )
    if template_path.exists():
        return template_path.read_text()
    return None


def upload_template(filename: str, content: str) -> bool:
    """Upload template to Azure Blob Storage via API"""
    url = f"{API_BASE}/api/v1/prompts/update/{REVISION_ID}/{filename}"
    payload = {"content": content}

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print(f"✅ Uploaded {filename}")
            return True
        else:
            print(f"❌ Failed to upload {filename}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading {filename}: {e}")
        return False


def main() -> None:
    print(f"Uploading bike-insights templates to revision: {REVISION_ID}")
    print("-" * 60)

    success_count = 0

    for filename in TEMPLATE_FILES:
        content = read_local_template(filename)
        if content:
            if upload_template(filename, content):
                success_count += 1
        else:
            print(f"⚠️  Template {filename} not found locally")

    print("-" * 60)
    print(f"Successfully uploaded {success_count}/{len(TEMPLATE_FILES)} templates")

    # Verify by listing templates
    try:
        response = requests.get(f"{API_BASE}/api/v1/prompts/list/{REVISION_ID}")
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ Verified: {data['count']} templates now available in Azure Blob Storage"
            )
            print("Available templates:", data["files"])
        else:
            print("❌ Could not verify template upload")
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")


if __name__ == "__main__":
    main()
