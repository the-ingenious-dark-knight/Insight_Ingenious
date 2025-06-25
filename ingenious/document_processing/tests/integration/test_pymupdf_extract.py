"""
Insight Ingenious — PyMuPDF integration tests
============================================

Purpose
-------
This module forms part of the **integration** test-suite for the
``ingenious.document_processing`` subsystem.  It validates the concrete
extractor that delegates PDF parsing to **PyMuPDF** (also known as *fitz*).

The checks cover four broad areas:

1. **Happy-path extraction** – A well-formed PDF must yield at least one element
   and each element must conform to the mandatory *Element* schema.
2. **Determinism** – Two consecutive calls with identical input must return
   byte-for-byte equivalent output, ensuring the absence of hidden global
   state.
3. **Input flexibility** – The extractor must accept three input forms:
   * ``Path`` to a file on disk
   * Raw ``bytes`` held entirely in memory
   * ``io.BytesIO`` stream (simulated in-memory file handle)
4. **Coordinate sanity** – The first element’s bounding box must lie inside a
   generous ``1 000 × 1 000`` user-space square, detecting unit mismatches or
   negative values early.

Fixtures
--------
``pymupdf`` (module-scoped)
    Yields a *single* extractor instance for all tests to avoid repeated native
    initialisation costs.
``pdf_path``, ``pdf_bytes``
    Shared fixtures (declared in ``conftest.py``) that supply the same sample
    PDF in different formats.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest

from ingenious.document_processing.extractor import _load

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
_MAX_COORD: int = 1_000  # upper bound for coarse coordinate sanity check


# --------------------------------------------------------------------------- #
# fixtures                                                                    #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pymupdf():
    """
    Yield a *single* PyMuPDF-backed extractor instance for the entire module.

    The underlying native library is expensive to load, therefore the extractor
    is instantiated once and shared across test functions.

    Yields
    ------
    ingenious.document_processing.extractor.DocumentExtractor
        Extractor whose :pyfunc:`~ingenious.document_processing.extractor.DocumentExtractor.extract`
        method uses PyMuPDF internally.
    """
    return _load("pymupdf")


# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #
def _assert_valid_element(el: dict[str, Any]) -> None:
    """
    Validate that *el* respects the mandatory *Element* schema.

    An *Element* produced by the document-processing API **must** include at
    minimum the following keys with the prescribed types:

    ==========  ==============  ================================
    Key         Expected type   Additional requirement
    ==========  ==============  ================================
    ``page``    ``int``         ``>= 1``
    ``type``    ``str``         Non-empty
    ``text``    ``str``         Non-empty
    ``coords``  ``tuple``       Four numeric values ``(x0, y0, x1, y1)``
    ==========  ==============  ================================

    Parameters
    ----------
    el
        Dictionary returned by the PyMuPDF extractor.

    Raises
    ------
    AssertionError
        If a required key is missing, the value type is incorrect, or a value
        expected to be non-empty is empty.

    Notes
    -----
    Centralising the validation logic keeps individual test functions concise
    while ensuring every schema violation triggers a clear, actionable failure
    message.
    """
    required = {"page", "type", "text", "coords"}
    missing = required.difference(el)
    assert not missing, f"element missing keys: {missing}"

    assert isinstance(el["page"], int) and el["page"] >= 1, "invalid page"
    assert isinstance(el["type"], str) and el["type"], "empty type"
    assert isinstance(el["text"], str) and el["text"], "empty text"

    coords = el["coords"]
    assert (
        isinstance(coords, tuple)
        and len(coords) == 4
        and all(isinstance(c, (int, float)) for c in coords)
    ), "coords must be a 4-tuple of numeric values"


# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #
def test_extract_from_path(pymupdf, pdf_path: Path) -> None:
    """
    Extract from a **file path** and verify idempotence.

    Workflow
    --------
    1. Invoke ``pymupdf.extract`` with *pdf_path* and collect every element.
    2. Validate each element via :pyfunc:`_assert_valid_element`.
    3. Call the extractor **again** with the same input and assert that the two
       result lists are identical.

    The final equality check detects hidden global state or time-dependent
    behaviour in the extractor.

    Parameters
    ----------
    pymupdf
        Fixture-supplied extractor instance.
    pdf_path
        Path to the reference PDF provided by ``conftest.py``.
    """
    els = list(pymupdf.extract(pdf_path))
    assert els, "no elements extracted"

    for el in els:
        _assert_valid_element(el)

    assert els == list(pymupdf.extract(pdf_path)), "extractor not idempotent"


def test_extract_from_bytes(pymupdf, pdf_bytes: bytes) -> None:
    """
    Extract directly from **raw bytes** stored in memory.

    The test ensures that at least one element is produced and that the first
    element meets the schema requirements.  Deeper validation is delegated to
    :pyfunc:`_assert_valid_element`.

    Parameters
    ----------
    pymupdf
        Fixture-supplied extractor instance.
    pdf_bytes
        Raw byte sequence representing the reference PDF.
    """
    els = list(pymupdf.extract(pdf_bytes))
    assert els, "no elements extracted from bytes"
    _assert_valid_element(els[0])


def test_extract_from_stream(pymupdf, pdf_bytes: bytes) -> None:
    """
    Extract from an **in-memory byte stream** (``io.BytesIO``).

    Rationale
    ---------
    PyMuPDF cannot open a :class:`io.BytesIO` object directly.  The extractor
    therefore buffers the stream into bytes, then delegates to the same code
    path exercised in :pyfunc:`test_extract_from_bytes`.  Passing an actual
    ``BytesIO`` instance guarantees that branch is covered by the test-suite.

    Parameters
    ----------
    pymupdf
        Fixture-supplied extractor instance.
    pdf_bytes
        Raw byte sequence representing the reference PDF.
    """
    stream = io.BytesIO(pdf_bytes)
    els = list(pymupdf.extract(stream))
    assert els, "no elements extracted from stream"
    _assert_valid_element(els[0])


def test_coord_range(pymupdf, pdf_path: Path) -> None:
    """
    Smoke-test the **coordinate range** of the first element.

    The bounding box is expected to lie within a ``1 000 × 1 000`` user-space
    square.  Extremely large or negative values often signal a unit mismatch
    (points versus pixels) or faulty parser logic, which downstream consumers
    (e.g. highlight renderers) may not tolerate.

    Parameters
    ----------
    pymupdf
        Fixture-supplied extractor instance.
    pdf_path
        Path to the reference PDF.

    Raises
    ------
    AssertionError
        If any coordinate falls outside the expected range.
    """
    els = list(pymupdf.extract(pdf_path))
    x0, y0, x1, y1 = els[0]["coords"]

    assert 0 <= x0 <= x1 <= _MAX_COORD, "x-coords out of range"
    assert 0 <= y0 <= y1 <= _MAX_COORD, "y-coords out of range"
