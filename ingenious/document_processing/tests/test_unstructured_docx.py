"""
Integration-smoke tests for the *unstructured* DOCX extractor.

Purpose
-------
These tests validate the public contract of the **unstructured** document
extractor that ships with Insight Ingenious.  They exercise a realistic
end-to-end path (loading the extractor through the registry, calling the
`.supports` capability probe, and running `.extract` on an actual DOCX file)
without inspecting internal implementation details.

Guarantees verified
-------------------
1. **Feature discovery** – `.supports` must answer *True* for:
   • a ``pathlib.Path`` instance pointing to a DOCX file
   • a raw ``str`` containing the same path
   Any other answer would prevent higher-level orchestration code from routing
   the file to the correct engine.

2. **Basic extraction** – `.extract` must yield at least one element whose
   ``"text"`` field is non-empty, proving that parsing succeeded.

3. **Determinism** – Calling `.extract` twice on the identical input must
   return identical results, guaranteeing idempotence and allowing safe
   caching.

Environment and fixtures
------------------------
* ``unstructured_available`` – Boolean fixture defined in the test suite that
  toggles these tests when the **unstructured** dependency is not installed.
* ``docx_path`` – Parameterised fixture that provides a path to a minimal,
  well-formed DOCX file stored in the repository’s test assets.

If **unstructured** is unavailable the entire module is skipped, ensuring the
test matrix remains green on environments where the optional dependency is
omitted.

This test file is intentionally lightweight and avoids deep semantic
assertions; exhaustive parsing accuracy is covered by engine-specific unit
tests elsewhere in the suite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ingenious.document_processing.extractor import _load


@pytest.fixture(scope="module")
def ux(unstructured_available: bool) -> Any:
    """
    Lazily load the *unstructured* extractor for the entire module.

    Parameters
    ----------
    unstructured_available
        Fixture that reports whether the optional *unstructured*
        third-party package is present in the current Python environment.

    Returns
    -------
    Any
        A fully initialised extractor instance registered under the key
        ``"unstructured"``.  The return type is *Any* because the concrete
        extractor class is discovered at runtime and is not imported here
        directly.

    Notes
    -----
    * If *unstructured* is missing, the call to :pyfunc:`pytest.skip`
      marks every test in this module as *skipped* rather than *failed*,
      which keeps optional feature coverage from blocking continuous
      integration pipelines.
    """
    if not unstructured_available:
        pytest.skip("unstructured not installed")
    return _load("unstructured")


# ────────────────────────────────────────────────────────────────────────────
# supports() contract
# ────────────────────────────────────────────────────────────────────────────
def test_supports_accepts_docx_path(ux: Any, docx_path: Path) -> None:
    """
    Ensure ``supports`` recognises both ``Path`` and ``str`` DOCX inputs.

    Rationale
    ---------
    The orchestration layer passes file references in both object forms,
    depending on how paths were constructed earlier in the pipeline.
    """
    assert ux.supports(docx_path) is True
    assert ux.supports(str(docx_path)) is True


# ────────────────────────────────────────────────────────────────────────────
# extraction contract
# ────────────────────────────────────────────────────────────────────────────
def test_extract_from_path(ux: Any, docx_path: Path) -> None:
    """
    Verify that at least one text element is produced from a DOCX file.

    Expectations
    ------------
    * The result of ``list(ux.extract(path))`` is non-empty.
    * At least one element in that list contains a truthy ``"text"`` field.
    """
    elements = list(ux.extract(docx_path))
    assert elements and any(el["text"] for el in elements)


def test_extract_is_idempotent(ux: Any, docx_path: Path) -> None:
    """
    Confirm that repeated extraction yields identical output.

    This guards against hidden mutable state inside the extractor that could
    produce divergent tokenisation or metadata on successive runs.
    """
    assert list(ux.extract(docx_path)) == list(ux.extract(docx_path))
