"""
Insight Ingenious – integration tests for AzureDocIntelligenceExtractor
======================================================================

This module contains **live** integration tests that exercise the
:class:`~ingenious.document_processing.extractor.azure_doc_intelligence.AzureDocIntelligenceExtractor`
(abbreviated throughout as *azdocint*).  Unlike unit tests that rely on
mocked responses, these tests submit real files to Azure AI Document
Intelligence’s *prebuilt-document* model and validate the structure of the
streamed output.

Motivation
----------

* Detect breaking changes in Azure’s service behaviour or API surface.
* Verify that authentication, network configuration, and extractor plumbing
  are working end-to-end in the current environment.
* Provide developers with a quick sanity check before publishing changes that
  affect the extractor.

How the tests work
------------------

1. For every sample filename in ``_SAMPLE_FILES`` a parametrised test case is
   generated.
2. The test case first calls :pyfunc:`_skip_if_invalid` which:

   * skips the test when the required environment variables are absent, and
   * skips the test when the sample asset is missing on disk.

3. The extractor’s :pyfunc:`ingenious.document_processing.extractor.base.DocumentExtractor.extract`
   coroutine is invoked through :pyfunc:`_run_extract`; the returned generator
   is fully materialised so that network errors surface immediately.
4. The resulting element list is asserted to be non-empty and each dictionary
   is checked for the mandatory ``page`` and ``text`` keys.

Environment variables
---------------------

=============================  ============================================
Variable                       Purpose
=============================  ============================================
``AZURE_DOC_INTEL_ENDPOINT``   Endpoint URL of the Azure resource
``AZURE_DOC_INTEL_KEY``        Resource key (primary or secondary)

*Legacy names*
``AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`` and
``AZURE_DOCUMENT_INTELLIGENCE_KEY`` are also respected for backward
compatibility.
=============================  ============================================

Sample assets
-------------

The test data directory ``tests/data_azure_doc_intell`` ships with four tiny
files that cover the most common input types:

* PDF document (born-digital)
* PNG, JPEG, and TIFF images containing printed text

Developers may add additional samples; just include the filename in
``_SAMPLE_FILES`` and commit the asset to the repository.

Usage
-----

Run the tests locally (assuming *pytest* is installed and the environment
variables are set)::

    uv run pytest -m integration tests/test_azure_doc_intelligence.py

The *integration* marker allows the suite to be excluded during
fast, offline unit-test runs.

Notes
-----

*Network calls* These tests make outbound HTTPS requests.  In CI pipelines
behind a proxy or strict firewall, ensure egress to
``*.cognitiveservices.azure.com`` is permitted.

*Cost* Each test processes a single-page document that stays well within the
free tier quotas of Azure AI Document Intelligence.  Even a full CI matrix run
should incur negligible cost.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pytest

from ingenious.document_processing.extractor import _load

# ---------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------
TEST_DATA_DIR = Path(__file__).parent / "data_azure_doc_intell"
# You need to create and populate this folder.
_SAMPLE_FILES = ("sample.pdf", "sample.png", "sample.jpg", "sample.tiff")

# ---------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def azdocint():
    """
    Provide a **module-scoped** AzureDocIntelligenceExtractor instance.

    Loading the extractor once per module avoids repeatedly constructing
    the underlying Azure client, which would be wasteful and slightly
    slower.

    Returns
    -------
    ingenious.document_processing.extractor.azure_doc_intelligence.AzureDocIntelligenceExtractor
        Fully initialised extractor ready to process documents.
    """
    return _load("azdocint")


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------
def _has_credentials() -> bool:
    """
    Check whether the environment contains both the endpoint and key.

    Returns
    -------
    bool
        ``True`` when authentication data is present; ``False`` otherwise.
    """
    endpoint_present = os.getenv("AZURE_DOC_INTEL_ENDPOINT") or os.getenv(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
    )
    key_present = os.getenv("AZURE_DOC_INTEL_KEY") or os.getenv(
        "AZURE_DOCUMENT_INTELLIGENCE_KEY"
    )
    return bool(endpoint_present and key_present)


def _skip_if_invalid(file_path: Path) -> None:
    """
    Skip the current test when prerequisites are not satisfied.

    The helper performs two independent checks:

    1. Authentication variables must be present.
    2. The sample file must exist on disk.

    Parameters
    ----------
    file_path :
        Absolute path to the sample asset needed by the test.

    Raises
    ------
    pytest.skip :
        Raised indirectly through :pyfunc:`pytest.skip` when a prerequisite
        is missing.
    """
    if not _has_credentials():
        pytest.skip("Azure credentials are not configured")
    if not file_path.exists():
        pytest.skip(f"Test asset not found: {file_path}")


def _run_extract(extractor, sample_path: Path) -> Iterable[dict]:
    """
    Execute the extractor against *sample_path* and return the full result.

    Parameters
    ----------
    extractor :
        Instance returned by :pyfunc:`azdocint`.
    sample_path :
        Local file path pointing to the document or image.

    Returns
    -------
    list[dict]
        Materialised list of element dictionaries emitted by the extractor.

    Notes
    -----
    Materialising the generator inside this helper ensures that any
    exceptions raised during iteration (network errors, data-parsing
    problems, etc.) propagate to the calling test case immediately.
    """
    return list(extractor.extract(sample_path))


# ---------------------------------------------------------------------
# integration tests
# ---------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.parametrize("sample_name", _SAMPLE_FILES)
def test_extract_document(azdocint, sample_name: str) -> None:
    """
    Validate extraction for each sample file listed in ``_SAMPLE_FILES``.

    The test asserts two conditions:

    1. The extractor returns at least one element.
    2. Every **non-table** element contains both ``page`` and ``text`` keys.

    Tables are skipped because they may legitimately omit ``text``.
    """
    sample_path = TEST_DATA_DIR / sample_name
    _skip_if_invalid(sample_path)

    elements = _run_extract(azdocint, sample_path)
    assert elements, f"No elements extracted from {sample_name}"

    non_table = [el for el in elements if str(el.get("type", "")).lower() != "table"]
    assert all("page" in el and "text" in el for el in non_table), (
        "At least one non-table element is missing the required keys"
    )
