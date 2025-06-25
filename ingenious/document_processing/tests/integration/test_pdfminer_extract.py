"""
Insight Ingenious — integration tests for the PdfMiner adapter
=============================================================

This module is part of the **integration** tier in the document-processing
test-suite.  It probes the adaptor that wraps *pdfminer.six* and exposes it
through :pyfunc:`ingenious.document_processing.extractor.extract`.

Objectives
----------
1. **Extraction sanity check**
   *At least one* element returned by the adaptor must contain visible text when
   parsing a well-formed reference PDF.  A zero-length result indicates a
   regression that would silently drop content in production.

2. **Deterministic behaviour**
   Running the extractor twice on identical input must yield byte-for-byte
   identical output.  Determinism underpins reproducible research, cache keys
   that depend on content digests, and straightforward debugging.

Fixtures
--------
* ``pdf_path`` – Path object pointing to a small, known-good sample PDF.
* ``pdfminer_available`` – Boolean flag signalling whether *pdfminer.six* is
  importable.  Tests are skipped gracefully on hosts where the dependency is
  missing.

The tests favour **clarity over cleverness**.  Assertions are intentionally
explicit so that any failure message conveys a clear cause.
"""

from pathlib import Path
from typing import List

import pytest

from ingenious.document_processing.extractor import _load

_EXTRACTOR_NAME = "pdfminer"


@pytest.mark.usefixtures("pdfminer_available")
def test_pdfminer_success(pdf_path: Path, pdfminer_available: bool) -> None:
    """
    Verify that the adaptor powered by PdfMiner extracts *some* text.

    Parameters
    ----------
    pdf_path
        Path to the sample PDF provided by the fixture.
    pdfminer_available
        Indicates whether *pdfminer.six* is installed on the test host.

    Behaviour
    ---------
    * If ``pdfminer_available`` is ``False`` the test is skipped.
    * Otherwise the extractor is invoked and the resulting list of element
      dictionaries is scanned for at least one non-empty ``"text"`` field.

    Raises
    ------
    AssertionError
        Raised when no element contains a non-empty ``"text"`` value,
        signalling that content extraction failed.
    """
    if not pdfminer_available:
        pytest.skip("pdfminer is not installed")

    pdfminer = _load(_EXTRACTOR_NAME)
    texts: List[str] = [element["text"] for element in pdfminer.extract(pdf_path)]

    assert any(texts), "PdfMiner extracted no text from a valid PDF"


def test_pdfminer_idempotent(pdf_path: Path, pdfminer_available: bool) -> None:
    """
    Confirm that the extractor is deterministic.

    Parameters
    ----------
    pdf_path
        Path to the sample PDF used for this check.
    pdfminer_available
        Indicates whether *pdfminer.six* is installed on the test host.

    Behaviour
    ---------
    * The extractor is called twice with identical input.
    * The two result lists are compared for exact equality.

    Raises
    ------
    AssertionError
        Raised when the two outputs differ, meaning the extractor exhibits
        non-deterministic behaviour.
    """
    if not pdfminer_available:
        pytest.skip("pdfminer is not installed")

    pdfminer = _load(_EXTRACTOR_NAME)
    first_run = list(pdfminer.extract(pdf_path))
    second_run = list(pdfminer.extract(pdf_path))

    assert first_run == second_run, "Extractor output is not deterministic"
