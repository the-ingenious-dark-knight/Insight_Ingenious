"""insight ingenious – DOCX‑support contract tests
=============================================

These *pytest* tests form an **executable specification** for the
``supports(path)`` behaviour promised by each document‑extractor engine
registered in :pyfile:`ingenious.document_processing.extractor`.  In
particular, the contract for **Microsoft Word** sources is:

* Engines that parse PDF **only** – currently *PyMuPDF* (``pymupdf``) and
  *pdfminer.six* (``pdfminer``) – **must** return ``False`` when asked whether
  they support a ``.docx`` file.  Advertising support they do not implement
  would route Word documents down a code path guaranteed to error later.
* The *unstructured* backend **does** implement Word support and therefore
  **must** return ``True`` for the same query.

Fail‑fast validation here prevents obscure run‑time failures deep inside the
processing pipeline and keeps the public API contract crystal‑clear.
"""

from __future__ import annotations

# ─────────────── third‑party ───────────────
import pytest

# ─────────────── first‑party ───────────────
from ingenious.document_processing.extractor import _load

__all__ = (
    "test_pdf_engines_reject_docx",
    "test_unstructured_accepts_docx",
)

# ───────────────────── tests ─────────────────────


@pytest.mark.parametrize(
    "engine_name",
    ("pymupdf", "pdfminer"),
    ids=("pymupdf rejects", "pdfminer rejects"),
)
def test_pdf_engines_reject_docx(engine_name: str) -> None:
    """A PDF‑only extractor must *not* advertise DOCX support.

    Parameters
    ----------
    engine_name
        Symbolic key for the extractor under test, as stored in
        :pydata:`~ingenious.document_processing.extractor._ENGINES`.

    Returns
    -------
    None
        The test passes silently when the assertion holds.

    Raises
    ------
    AssertionError
        If ``supports("file.docx")`` unexpectedly returns ``True`` for the
        given PDF‑only engine.
    """
    assert _load(engine_name).supports("file.docx") is False, (
        f"{engine_name} should return False for DOCX support"
    )


def test_unstructured_accepts_docx() -> None:
    """The *unstructured* backend **must** report DOCX capability.

    Returns
    -------
    None
        The test passes silently when the behaviour matches the contract.

    Raises
    ------
    AssertionError
        If the backend returns ``False``, indicating a regression in DOCX
        support.
    """
    assert _load("unstructured").supports("file.docx") is True, (
        "unstructured should return True for DOCX support"
    )
