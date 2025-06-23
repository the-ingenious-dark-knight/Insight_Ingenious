"""
Integration tests for the **PdfMiner**‐based document extractor.

These tests exercise the public extraction interface provided by
``ingenious.document_processing.extractor._load("pdfminer")`` and validate
its behaviour under three common scenarios:

1. **Happy-path extraction** – A valid PDF file is parsed and returns at least
   one text element.
2. **Invalid-input handling** – Supplying invalid / non-PDF bytes should fail
   gracefully and yield an empty iterable (rather than raising).
3. **Idempotency** – Re-running the extractor on the same file should return
   identical results, ensuring deterministic output for caching or hashing
   strategies.

Each test is automatically skipped when the optional *pdfminer* dependency is
unavailable (mediated by the ``pdfminer_available`` fixture).  This makes the
suite safe to run in minimal CI environments where PdfMiner may be excluded.

Fixtures expected from *conftest.py* (or other shared fixture modules)
------------------------------------------------------------------------
pdf_path
    ``pathlib.Path`` pointing to a small sample PDF stored in the test data
    directory.

pdfminer_available
    ``bool`` indicating whether **pdfminer.six** can be imported.  When
    *False*, tests are skipped rather than failed.

"""

import pytest

from ingenious.document_processing.extractor import _load


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
@pytest.mark.usefixtures("pdfminer_available")
def test_pdfminer_success(pdf_path, pdfminer_available):
    """
    Ensure that the PdfMiner extractor returns at least one non-empty text
    element when given a valid PDF file.

    Steps
    -----
    1. Skip if PdfMiner is not installed.
    2. Load the extractor via the internal registry helper ``_load``.
    3. Call ``extract`` with *pdf_path*.
    4. Collect the ``"text"`` field of every returned element.
    5. Assert that at least one element contains text.

    The assertion guards against silent failures where an extractor might
    return zero elements without throwing an exception.
    """
    if not pdfminer_available:
        pytest.skip("pdfminer not installed")

    pdfminer = _load("pdfminer")
    texts = [element["text"] for element in pdfminer.extract(pdf_path)]

    assert any(texts), "PdfMiner extracted no text from a valid PDF"


def test_pdfminer_invalid_bytes_returns_empty(pdfminer_available):
    """
    Verify graceful degradation when the extractor receives malformed data.

    Passing a ``bytes`` object that is **not** a PDF should not raise but
    instead return an empty iterator, enabling callers to handle failures
    uniformly without try/except blocks.
    """
    if not pdfminer_available:
        pytest.skip("pdfminer not installed")

    pdfminer = _load("pdfminer")
    result = list(pdfminer.extract(b"broken"))

    assert result == [], "Extractor should return an empty list on bad input"


def test_pdfminer_idempotent(pdf_path, pdfminer_available):
    """
    Confirm that multiple invocations with the **same** source yield identical
    results (idempotency).

    Deterministic output is critical for:
    * Caching layers that rely on content hashing.
    * Tests that compare saved snapshots against fresh parses.
    * Workflows that merge or diff successive extractions.

    The test executes ``extract`` twice and asserts equality of the resulting
    lists.
    """
    if not pdfminer_available:
        pytest.skip("pdfminer not installed")

    pdfminer = _load("pdfminer")
    first = list(pdfminer.extract(pdf_path))
    second = list(pdfminer.extract(pdf_path))

    assert first == second, "Extractor output is not deterministic"
