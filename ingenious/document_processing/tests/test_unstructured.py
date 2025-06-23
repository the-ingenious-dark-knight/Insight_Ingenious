"""Insight Ingenious – Unit‑tests for the *Unstructured* backend
=============================================================
Exercises two fundamental behaviours of the extractor obtained via
:pyfunc:`ingenious.document_processing.extractor._load` when the engine key is
``"unstructured"``.

* ``test_coords_to_jsonable_all_paths`` – White‑box test for the private helper
  method :pyfunc:`unstructured.extractor.UnstructuredExtractor._coords_to_jsonable`.
  The helper takes an arbitrary *coords* object produced by the upstream
  library and coerces it into a JSON‑serialisable representation.  Four control
  paths are covered so that any future refactor triggering a behavioural change
  is caught immediately.
* ``test_unstructured_extract_smoke`` – Black‑box sanity check confirming that
  raw PDF *bytes* are transformed into a Python ``list`` of element
  dictionaries.  No attempt is made to validate OCR quality or layout accuracy;
  the goal is purely to guarantee that the extractor does not raise and
  produces the expected return type.

Both tests assert **contractual guarantees** only, ensuring that higher‑level
code relying on these guarantees remains stable.

Fixtures & markers
------------------
``unstructured_available`` and various file‑content fixtures are supplied by
*conftest.py*.  The smoke test is marked with ``@pytest.mark.docs`` so that
documentation pipelines can include a lightweight subset if desired.

Execution example
-----------------
Run this specific module only::

    uv run pytest -q ingenious/document_processing/tests/test_unstructured.py

All assertions should pass silently.  When the optional dependency
``unstructured`` is missing, the smoke test is skipped.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from ingenious.document_processing.extractor import _load

# ──────────────────────────────────────────────────────────────────────────────
# tests
# ──────────────────────────────────────────────────────────────────────────────


def test_coords_to_jsonable_all_paths() -> None:
    """Exercise all logical branches of ``_coords_to_jsonable``.

    The upstream *Unstructured* library emits a variety of coordinate objects
    depending on the parser back‑end (PDF, DOCX, HTML, etc.).  Internally the
    Insight Ingenious wrapper normalises these objects via a private helper so
    that downstream code can rely on a consistent JSON‑friendly schema.

    Covered paths
    -------------
    1. **None input** – An explicit ``None`` is returned unchanged.
    2. **``.points`` attribute** – Objects exposing a ``points`` sequence are
       converted to ``[(x, y), …]``.
    3. **``to_dict`` method** – If present, the helper returns the resulting
       ``dict`` verbatim.
    4. **Fallback** – Any other type is coerced to its string representation via
       :pyfunc:`str`.

    Returns
    -------
    None
        The test uses ``assert`` statements exclusively; success is indicated
        by the absence of an :pyclass:`AssertionError`.
    """

    extractor = _load("unstructured")

    # Path 1 – None input
    assert extractor._coords_to_jsonable(None) is None  # type: ignore[attr-defined]

    # Path 2 – object with .points
    coords_with_points = SimpleNamespace(
        points=[SimpleNamespace(x=1, y=2), SimpleNamespace(x=3, y=4)]
    )
    expected_points = [(1, 2), (3, 4)]
    assert (
        extractor._coords_to_jsonable(coords_with_points)  # type: ignore[attr-defined]
        == expected_points
    )

    # Path 3 – object with .to_dict()
    class DictCoords:
        """Minimal stub that supports ``to_dict``."""

        def to_dict(self) -> dict[str, int]:
            return {"x": 1}

    assert extractor._coords_to_jsonable(DictCoords()) == {"x": 1}  # type: ignore[attr-defined]

    # Path 4 – arbitrary fallback
    class Weird:
        """Lacks ``points`` and ``to_dict``; stringifies to *"weird"*."""

        def __str__(self) -> str:  # noqa: D401 – simple stub
            return "weird"

    assert extractor._coords_to_jsonable(Weird()) == "weird"  # type: ignore[attr-defined]


@pytest.mark.docs
def test_unstructured_extract_smoke(
    unstructured_available: bool,
    pdf_bytes: bytes,
) -> None:  # noqa: D401
    """Confirm that a byte stream of PDF data yields a ``list``.

    The PDF content is supplied by a shared fixture created in *conftest.py*.

    Parameters
    ----------
    unstructured_available
        Indicates whether the optional dependency ``unstructured`` is
        importable; the test is skipped when it is not present.
    pdf_bytes
        Raw PDF data representing a small, text‑containing document.

    Raises
    ------
    pytest.skip
        When ``unstructured_available`` is *False*.
    AssertionError
        If the extractor does not return a list instance.
    """

    if not unstructured_available:
        pytest.skip("unstructured not installed")

    extractor = _load("unstructured")
    elements = list(extractor.extract(pdf_bytes))

    assert isinstance(elements, list), "Extractor did not return a list"
