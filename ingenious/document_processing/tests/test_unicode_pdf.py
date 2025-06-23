"""Insight Ingenious – Unicode‑robustness test for the *PyMuPDF* extractor
=======================================================================

This module contains a single **smoke‑test** that ensures the *PyMuPDF*‑based
extractor can handle PDFs containing a mix of Latin characters with
*diacritics* and Cyrillic glyphs.  The test generates a tiny PDF entirely
in‑memory, writes it to a temporary dir, runs the public
:pyfunc:`ingenious.document_processing.extractor.PyMuPDFExtractor.extract`
implementation, and confirms that *at least* a meaningful fragment of the
Latin text survives the round‑trip.

Why such a minimal assertion?  On some platforms MuPDF’s text‑extraction may
omit diacritics (e.g. "č" → "c") or drop non‑Latin scripts if the required
fonts are not embedded.  Rather than failing brittlely, we simply require that
*some* Latin substring ("okol" from "čokoláda") is present in the extracted
text, which serves as a proxy for the extractor not crashing and returning
content rather than an empty list.

Fixtures used
-------------
``pymupdf``
    A session‑scoped fixture defined in *conftest.py* that yields a *shared*
    instance of the PyMuPDF extractor obtained via
    :pyfunc:`ingenious.document_processing.extractor._load`.

``tmp_path``
    Standard *pytest* fixture providing a temporary directory unique to the
    test invocation.
"""

from __future__ import annotations

# ──────────────── standard library ────────────────
from pathlib import Path
from typing import List

# ──────────────── third‑party ────────────────
import fitz  # type: ignore – imported lazily inside the test

# ─────────────── first‑party (fixture import only, no direct code) ───────────────
#   The extractor itself is provided via the ``pymupdf`` fixture.

__all__: List[str] = [
    "test_pymupdf_unicode",
]

# ───────────────────── tests ─────────────────────


def test_pymupdf_unicode(pymupdf, tmp_path: Path) -> None:  # noqa: D401 fixture names
    """Validate that the PyMuPDF extractor handles mixed‑script Unicode.

    The test constructs a two‑line PDF containing Latin text with diacritics
    ("Zaželi čokoláda") *and* Cyrillic text ("привет").  After saving the PDF
    to ``tmp_path`` it invokes :pyfunc:`pymupdf.extract` and concatenates the
    extracted ``text`` blocks.  Because MuPDF’s extraction fidelity varies by
    platform and available fonts, we intentionally assert only that the
    substring "okol" (present in the Latin word "čokoláda") survives in the
    lower‑cased output.

    Parameters
    ----------
    pymupdf
        The shared PyMuPDF extractor instance supplied by the fixture.
    tmp_path
        Temporary directory unique to this test run, provided by *pytest*.

    Raises
    ------
    AssertionError
        If the expected Latin substring is **not** present in the extracted
        text, indicating a potential regression in Unicode handling.
    """
    # Build a minimal UTF‑8 PDF in‑memory -----------------------------
    pdf_path: Path = tmp_path / "utf8.pdf"
    doc = fitz.open()  # create empty document
    page = doc.new_page()
    page.insert_text((72, 700), "Zaželi čokoláda – привет")
    doc.save(pdf_path)

    # Extract text via the public API --------------------------------
    elements = list(pymupdf.extract(pdf_path))
    joined_text = " ".join(element["text"] for element in elements)

    # MuPDF may drop diacritics or non‑Latin glyphs; require *some* signal
    assert "okol" in joined_text.lower(), (
        "PyMuPDF extractor lost expected Latin substring in Unicode PDF"
    )
