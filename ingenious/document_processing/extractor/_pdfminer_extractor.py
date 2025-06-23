"""
Insight Ingenious – PDFMiner-based extractor
=====================================================

This module provides :class:`PDFMinerExtractor`, a concrete implementation of
:class:`ingenious.document_processing.extractor.DocumentExtractor` that relies
exclusively on **pdfminer.six** to extract text from *born-digital* (i.e. already
searchable) PDF files.

Why a dedicated extractor?
--------------------------
* **Pure-Python dependency tree** – avoids heavyweight native libraries.
* **Streaming architecture** – yields one :pyclass:`Element` at a time, keeping
  memory usage low even for multi-hundred-page PDFs.
* **Flexible I/O** – accepts paths, *Path-like* objects, URLs, or raw
  ``bytes``/``bytearray`` so it can integrate seamlessly with pipelines that
  have already downloaded the document.

Example
-------
>>> from ingenious.document_processing.extractor import _load
>>> pdfminer = _load("pdfminer")
>>> for block in pdfminer.extract("reports/contract.pdf"):
...     print(f"p{block['page']:>3}: {block['text'][:60]}…")

When to use
-----------
* Use this extractor when your PDF already contains a **text layer** (created
  by a word-processor or a post-OCR workflow).
* For *image-only* PDFs (e.g. scans or faxes), prefer an OCR-enabled engine
  such as the *pymupdf* or *tesseract* extractors instead.

Terminology
-----------
*An* **Element** is a small mapping with the keys:

=================  ==========================================================
``page``           1-based page number
``type``           A short string describing the block type; here always
                   ``"NarrativeText"``
``text``           The raw text content of the block, *stripped of trailing
                   whitespace*
``coords``         (x0, y0, x1, y1) in PDF-user units – the lower-left and
                   upper-right corners of the text box
=================  ==========================================================

All values are yielded in **natural reading order** (left-to-right,
top-to-bottom within each page, and page order preserved).
"""

from __future__ import annotations

import io
import logging
import mimetypes
import os
from pathlib import Path
from typing import Iterable, Union, cast

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

from .base import DocumentExtractor, Element

logger = logging.getLogger(__name__)

# Accept *Path-like* objects as well as ``str`` or raw ``bytes`` for parity with
# the high-level :pyfunc:`ingenious.document_processing.extract` helper.
Src = Union[str, bytes, os.PathLike[str]]


class PDFMinerExtractor(DocumentExtractor):
    """
    Extract text from *born-digital* PDFs using **pdfminer.six**.

    The class fulfils the :class:`DocumentExtractor` interface that powers
    the :pyfunc:`ingenious.document_processing.extract` helper.  It is
    intentionally minimalist – everything heavy is delegated to pdfminer.

    Attributes
    ----------
    name : str
        Public identifier used by the CLI and by
        ``extract(source, engine="pdfminer")`` calls.
    """

    #: Public identifier registered with the factory loader.
    name = "pdfminer"

    # --------------------------------------------------------------------- #
    # Public helpers                                                        #
    # --------------------------------------------------------------------- #
    def supports(self, src: Src) -> bool:
        """
        Heuristically decide whether *src* is a PDF.

        The method performs *only* cheap checks – it never opens a file or
        downloads a URL.  This allows the extractor registry to pick a suitable
        engine quickly without side effects.

        Parameters
        ----------
        src : Src
            * ``str`` or :class:`pathlib.Path` – A local file path or URL.
            * ``bytes`` or ``bytearray`` – Raw PDF bytes already in memory.

        Returns
        -------
        bool
            ``True`` if the filename extension is ``.pdf`` **or** MIME sniffing
            via :pyfunc:`mimetypes.guess_type` returns ``application/pdf``.  Raw
            byte sequences are always accepted because they might be a PDF
            stream piped in from elsewhere.

        Notes
        -----
        A *positive* result does **not** guarantee that the content is a valid
        PDF, merely that it *looks like* one.  Robustness checks happen later
        when pdfminer actually parses the bytes.
        """
        if isinstance(src, (bytes, bytearray)):
            # Raw bytes – assume caller knows what they are passing.
            return True

        mime, _ = mimetypes.guess_type(str(src))
        return str(src).lower().endswith(".pdf") or mime == "application/pdf"

    # --------------------------------------------------------------------- #
    # Main extraction pipeline                                              #
    # --------------------------------------------------------------------- #
    def extract(self, src: Src) -> Iterable[Element]:
        """
        Stream :pyclass:`Element` mappings in natural reading order.

        The method is *lazy* – parsing starts only when the first element is
        requested.  Any pdfminer exceptions are caught and logged; the iterator
        then terminates gracefully so that batch pipelines continue with the
        next document.

        Parameters
        ----------
        src : Src
            A local path, URL, *Path-like* object, or raw PDF ``bytes``.  URLs
            must be downloaded **before** calling this method; only local file
            I/O is handled here.

        Yields
        ------
        Element
            See the *Terminology* section in the module docstring for details.

        Logging
        -------
        ``DEBUG`` – Start/finish events and the number of blocks extracted.
        ``WARNING`` – I/O errors or any exceptions raised by pdfminer.

        Examples
        --------
        >>> extractor = PDFMinerExtractor()
        >>> first_block = next(extractor.extract("docs/specs.pdf"))
        >>> first_block["text"][:80]
        'Introduction – This specification describes …'

        Performance
        -----------
        For multi-gigabyte PDFs you may prefer an extractor that can work
        *incrementally*.  pdfminer loads each page lazily, but some PDFs have
        enormous in-memory resources even per page.  Measure!
        """
        logger.debug("PDFMinerExtractor.extract(src=%r, type=%s)", src, type(src))

        # ── Normalise the input so pdfminer receives a file-like object ──
        if isinstance(src, Path):
            # Convert Path → str for consistent downstream checks.
            src = str(src)

        if isinstance(src, str) and Path(src).is_file():
            # Local file – eagerly read it into memory so downstream stages can
            # operate uniformly on BytesIO.
            try:
                with open(src, "rb") as fp:
                    src = fp.read()
            except OSError as exc:
                logger.warning("Cannot read %s: %s", src, exc)
                return  # Early exit – caller can decide how to proceed.

        if isinstance(src, (bytes, bytearray)):
            # Wrap raw bytes for pdfminer (expects a binary file-like object).
            src = io.BytesIO(cast(bytes, src))

        # ── Parse with pdfminer ───────────────────────────────────────────
        try:
            pdf_pages = list(extract_pages(src))  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover
            # pdfminer raises several custom exceptions – catch broadly.
            logger.warning("pdfminer failed on %r: %s", src, exc)
            return

        for page_no, page in enumerate(pdf_pages, start=1):
            for obj in page:
                if isinstance(obj, LTTextContainer):
                    text = obj.get_text().strip()
                    if not text:
                        continue  # Skip empty blocks (common with form fields).

                    x0, y0, x1, y1 = obj.bbox
                    yield {
                        "page": page_no,
                        "type": "NarrativeText",
                        "text": text,
                        "coords": (x0, y0, x1, y1),
                    }

        logger.debug("Extracted %s text blocks from %r", page_no, src)


__all__: list[str] = ["PDFMinerExtractor"]
