"""Insight Ingenious – extractor **resilience** tests
====================================================
This module validates how the *PDF extraction back‑ends* react when they
receive **invalid or deliberately corrupted byte streams** instead of a
well‑formed PDF. The goal is two‑fold:

1. **Integrity contract** – Certain engines (e.g. *PyMuPDF*, *PDFMiner*) are
   expected to *fail‑soft* and simply yield an empty iterator when content
   cannot be parsed. This ensures that higher‑level pipelines can skip bad
   documents without special casing every extractor.
2. **Error‑surface contract** – Other engines (currently only the
   *Unstructured* backend) intentionally propagate the underlying parser
   exception. We mark these paths with **`pytest.xfail`** so the behaviour is
   documented and monitored but does not break the CI.

Why do we exclude *Unstructured* from the lossless group?
--------------------------------------------------------
`partition_pdf` (used under the hood) invokes **`pdf2image`**, which raises
:pyclass:`pdf2image.exceptions.PDFPageCountError` on malformed input. That
is an explicit design choice of that dependency, and Insight Ingenious
surfaces it unchanged.

Running the tests
-----------------
Use the project‑wide helper:

```bash
uv run pytest ingenious/document_processing/tests/test_extract_corrupt_inputs.py
```

Fixtures provided by other `conftest.py` files are *not* required here.
"""

from __future__ import annotations

import pytest

from ingenious.document_processing.extractor import _ENGINES, extract

# --------------------------------------------------------------------------- #
# fixtures                                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="function")
def corrupt_pdf_bytes() -> bytes:  # noqa: D401  (imperative form is intentional)
    """Return a **minimal but invalid** PDF byte sequence.

    The sequence consists of a dummy *%PDF* header followed by an early
    *%%EOF* marker, guaranteeing that every compliant PDF parser will treat
    the stream as corrupt.
    """

    return b"%PDF-1.7 corrupted\n%%EOF"


# --------------------------------------------------------------------------- #
# engines that **promise** “empty list, no exception” on bad bytes            #
# --------------------------------------------------------------------------- #

LOSSLESS_ENGINES = [
    e for e in _ENGINES if e != "unstructured"
]  # ← see module docstring for rationale


@pytest.mark.parametrize("engine", LOSSLESS_ENGINES)
def test_extract_corrupt_bytes_returns_empty(engine: str, corrupt_pdf_bytes: bytes):
    """Engines advertised as *lossless* must return an **empty iterator**.

    - **Given**    an engine in :pydata:`LOSSLESS_ENGINES`
    - **When**     :pyfunc:`ingenious.document_processing.extractor.extract` is
      called with malformed PDF bytes
    - **Then**     the function yields no elements **and** raises no
      exception, allowing the caller to proceed gracefully.
    """

    assert list(extract(corrupt_pdf_bytes, engine=engine)) == []


# --------------------------------------------------------------------------- #
# Unstructured has a different contract: it escalates an upstream error      #
# --------------------------------------------------------------------------- #


@pytest.mark.xfail(
    reason=(
        "Unstructured routes raw bytes through `partition_pdf`, which raises "
        "pdf2image.PDFPageCountError on corrupt or non-PDF bytes. "
        "This is expected behaviour for that backend."
    ),
    raises=Exception,
)
def test_unstructured_corrupt_bytes_raises(corrupt_pdf_bytes: bytes):
    """Ensure *Unstructured* propagates the parser exception as designed."""

    extract(corrupt_pdf_bytes, engine="unstructured")
