"""
Smoke‑tests for the *Unstructured* extractor against **local PDF files** and raw
byte‑streams.

This module verifies the integrity and basic correctness of the
:pyclass:`ingenious.document_processing.extractor.UnstructuredExtractor` (loaded
indirectly via :pyfunc:`ingenious.document_processing.extractor._load`).  It
intentionally mirrors the coverage provided for the PyMuPDF‑ and PDFMiner‑based
extractors so that all back‑ends are held to the same baseline guarantees.

Rationale
~~~~~~~~~
The *Unstructured* back‑end parses PDFs into a list of dictionaries, one per
layout block, with a minimal schema::

    {
        "page": int,  # 1‑based page index
        "type": str,  # block kind, e.g. "NarrativeText", "Title", ...
        "text": str,  # textual content (may be empty for layout‑only blocks)
        ...           # implementation‑specific extras are ignored by tests
    }

While the library is powerful, it introduces an external, optional dependency.
These tests therefore focus on *contract* rather than *performance*:

1. Execution does not fail when the dependency is available.
2. At least one block contains non‑empty text for ordinary documents.
3. Re‑running with identical input yields byte‑wise identical results (idempotent).
4. The schema rules above hold when the extractor receives raw bytes instead of
   a file‑path.

Skipping Strategy
-----------------
The entire module is skipped when the fixture ``unstructured_available`` is
``False``.  This pattern keeps the *default* CI matrix lightweight while still
allowing downstream projects to enable the extra coverage simply by installing
``unstructured`` in the test environment.

Example
~~~~~~~
Run the tests for this specific module only::

    uv run pytest -q ingenious/document_processing/tests/test_unstructured_extract.py

All assertions should pass silently, indicating that the extractor meets the
minimum quality bar established by Insight Ingenious.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from ingenious.document_processing.extractor import _load


# ──────────────────────────────────────────────────────────────────────────────
# fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def ux(unstructured_available: bool):  # type: ignore[valid-type]
    """Return a lazily‑loaded instance of the *Unstructured* extractor.

    The fixture defers the potentially expensive import until the test session
    actually needs it.  When the optional dependency is missing, the entire
    module is marked as *skipped* so that CI passes in minimal environments.

    Parameters
    ----------
    unstructured_available
        Supplied by ``conftest.py``; ``True`` when the package
        ``unstructured`` is importable.

    Returns
    -------
    Any
        A ready‑to‑use extractor whose public API matches the contract defined
        in :pyfunc:`ingenious.document_processing.extractor._load`.
    """

    if not unstructured_available:
        pytest.skip("unstructured not installed")
    return _load("unstructured")


# ──────────────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────────────
_TEXT_REQUIRED_TYPES: set[str] = {
    "narrativetext",
    "paragraph",
    "title",
    "head",
}


def _assert_valid_element(el: Dict[str, Any]) -> None:
    """Assert that *el* conforms to the minimal extractor schema.

    Parameters
    ----------
    el
        Element dictionary emitted by the extractor under test.

    Raises
    ------
    AssertionError
        If a field is missing, of the wrong type, or semantically invalid.

    Notes
    -----
    The predicate allows *layout‑only* elements whose ``text`` value is an
    empty string, except for block kinds listed in ``_TEXT_REQUIRED_TYPES``.
    """

    # Structural checks
    assert isinstance(el["page"], int) and el["page"] >= 1, "Invalid page number"
    assert isinstance(el["type"], str) and el["type"], "Missing block type"
    assert isinstance(el["text"], str), "Text field must always be present"

    # Content check for text‑bearing block kinds
    if el["type"].lower() in _TEXT_REQUIRED_TYPES:
        assert el["text"], f"Expected non‑empty text for {el['type']}"


# ──────────────────────────────────────────────────────────────────────────────
# tests
# ──────────────────────────────────────────────────────────────────────────────


def test_extract_from_path(ux, pdf_path):
    """Extractor yields at least one valid element for a *Path* input.

    The PDF referenced by *pdf_path* is part of the shared pytest fixtures and
    guaranteed to contain text.  We iterate over the result once because
    ``_load`` returns a generator; converting to ``list`` exhausts it for easy
    assertions.
    """
    els = list(ux.extract(pdf_path))
    assert els, "No elements extracted from local PDF"
    for el in els:
        _assert_valid_element(el)


def test_extract_from_path_idempotent(ux, pdf_path):
    """Calling ``.extract`` twice with the same *Path* yields identical lists."""
    assert list(ux.extract(pdf_path)) == list(ux.extract(pdf_path))


def test_extract_from_bytes_schema(unstructured_available, pdf_bytes):
    """Schema invariants hold when the extractor consumes raw *bytes*.

    The helper fixture ``pdf_bytes`` provides the contents of the same PDF used
    in the path‑based tests.  We re‑load the extractor locally instead of using
    the *module‑scoped* ``ux`` fixture to verify that repeated instantiation is
    safe.
    """
    if not unstructured_available:
        pytest.skip("unstructured not installed")

    ux_local = _load("unstructured")
    for el in ux_local.extract(pdf_bytes):
        _assert_valid_element(el)
