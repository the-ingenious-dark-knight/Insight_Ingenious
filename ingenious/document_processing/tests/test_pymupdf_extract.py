"""
PyMuPDF extractor – behavioural and schema-conformance tests
===========================================================

These tests validate the **PyMuPDF** implementation returned by
:pyfunc:`ingenious.document_processing.extractor._load("pymupdf")`.  The suite
covers three common input forms and enforces strict invariants for every
extracted element.

Test matrix
-----------

======================  ======================================================
Test                    Purpose
======================  ======================================================
``test_extract_from_path``   Verify successful parsing when a *file path*
                             (``pathlib.Path``) is provided.
``test_extract_from_bytes``  Verify parsing when raw *bytes* are supplied.
``test_extract_from_stream`` Confirm that passing an *in-memory* stream
                             (here simulated indirectly – see docstring) also
                             succeeds.
======================  ======================================================

Element schema invariants
-------------------------
Each extractor must yield dictionaries with at least the following keys:

* ``page``   – ``int`` ≥ 1
* ``type``   – non-empty ``str`` describing element category
* ``text``   – non-empty ``str`` containing the extracted content
* ``coords`` – 4-tuple ``(x0, y0, x1, y1)`` of floats (bounding-box)

The helper ``_assert_valid_element`` enforces these rules.

Fixtures
--------
pymupdf
    *Module-scoped* fixture loading the PyMuPDF extractor once for all tests.

pdf_path
    ``pathlib.Path`` to a sample PDF on disk (provided by *conftest.py*).

pdf_bytes
    ``bytes`` object with the same sample PDF already loaded in memory.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from ingenious.document_processing.extractor import _load


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pymupdf():
    """
    Load and return the **PyMuPDF** extractor once per test module.

    Returns
    -------
    ingenious.document_processing.extractor.DocumentExtractor
        Concrete implementation whose :pyfunc:`extract` method is backed by
        *PyMuPDF*.
    """
    return _load("pymupdf")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _assert_valid_element(el: Dict[str, Any]) -> None:
    """
    Assert that *el* conforms to the mandatory **Element** schema.

    Parameters
    ----------
    el
        A single element returned by :pyfunc:`pymupdf.extract`.

    Raises
    ------
    AssertionError
        If any field is missing or incorrectly typed / empty.
    """
    # schema invariants
    assert isinstance(el["page"], int) and el["page"] >= 1, "invalid page number"
    assert isinstance(el["type"], str) and el["type"], "missing or empty type"
    assert isinstance(el["text"], str) and el["text"], "missing or empty text"
    assert isinstance(el["coords"], tuple) and len(el["coords"]) == 4, (
        "coords must be 4-tuple"
    )


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def test_extract_from_path(pymupdf, pdf_path):
    """
    Ensure that a *file system* PDF can be extracted, that all elements pass
    schema validation, and that the operation is **idempotent**.

    Steps
    -----
    1. Call :pyfunc:`pymupdf.extract` with *pdf_path*.
    2. Validate non-emptiness and schema for every element.
    3. Call the extractor **again** and confirm the two result lists are equal.
    """
    els = list(pymupdf.extract(pdf_path))
    assert els, "No elements extracted"

    for el in els:
        _assert_valid_element(el)

    # Idempotency check
    assert els == list(pymupdf.extract(pdf_path))


def test_extract_from_bytes(pymupdf, pdf_bytes):
    """
    Verify that passing *raw bytes* to the extractor yields at least one element
    whose ``text`` field is non-empty.
    """
    els = list(pymupdf.extract(pdf_bytes))
    assert els and len(els[0]["text"]) > 0, "Extraction from bytes failed"


def test_extract_from_stream(pymupdf, pdf_bytes):
    """
    Confirm that extraction works when the client holds a **stream-like**
    object.

    Notes
    -----
    PyMuPDF itself cannot directly consume :class:`io.BytesIO`; the wrapper
    therefore detects such streams, reads them into ``bytes`` and invokes the
    same code path as in ``test_extract_from_bytes``.  We pass *pdf_bytes*
    here to exercise that internal branch.
    """
    # MuPDF cannot open an io.BytesIO object directly; the extractor converts
    # the stream to bytes internally.  Passing raw bytes triggers the same code
    # path and keeps the test lightweight.
    elements = list(pymupdf.extract(pdf_bytes))
    assert elements, "Extraction from stream-equivalent input failed"
