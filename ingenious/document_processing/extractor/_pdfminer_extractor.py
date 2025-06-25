"""
Insight Ingenious – PDFMiner-based extractor
===========================================

This module provides :class:`PDFMinerExtractor`, a concrete implementation of
:class:`ingenious.document_processing.extractor.DocumentExtractor` that relies
exclusively on **pdfminer.six** to extract text from *born-digital* (i.e.
already searchable) PDF files.

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
from contextlib import suppress
from pathlib import Path
from typing import Iterable, Union, cast

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFSyntaxError

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

    # ------------------------------------------------------------------ #
    # Public helpers                                                     #
    # ------------------------------------------------------------------ #
    def supports(self, src: Src) -> bool:
        """
        Heuristically decide whether *src* is a PDF.

        The method performs *only* cheap checks – it never opens a file or
        downloads a URL.  This allows the extractor registry to pick a suitable
        engine quickly without side effects.

        Parameters
        ----------
        src : Src
            * ``str`` or :class:`pathlib.Path`` – A local file path or URL.
            * ``bytes`` or ``bytearray`` – Raw PDF bytes already in memory.

        Returns
        -------
        bool
            ``True`` if the filename extension is ``.pdf`` **or** MIME sniffing
            via :pyfunc:`mimetypes.guess_type` returns ``application/pdf``.  Raw
            byte sequences are always accepted because they might be a PDF
            stream piped in from elsewhere.
        """
        if isinstance(src, (bytes, bytearray)):
            return True

        mime, _ = mimetypes.guess_type(str(src))
        return str(src).lower().endswith(".pdf") or mime == "application/pdf"

    # ------------------------------------------------------------------ #
    # Main extraction pipeline                                           #
    # ------------------------------------------------------------------ #
    def extract(self, src: Src) -> Iterable[Element]:
        """
        Stream :pyclass:`Element` mappings in natural reading order.

        The method is *lazy* – parsing starts only when the first element is
        requested.  Corruption-related pdfminer exceptions are suppressed so
        that malformed documents fail soft and yield nothing.

        Parameters
        ----------
        src : Src
            A local path, URL, *Path-like* object, or raw PDF ``bytes``.  URLs
            must be downloaded **before** calling this method; only local file
            I/O is handled here.
        """
        logger.debug("PDFMinerExtractor.extract(src=%r, type=%s)", src, type(src))

        # ── Normalise input so pdfminer receives a file-like object ──
        if isinstance(src, Path):
            src = str(src)

        if isinstance(src, str) and Path(src).is_file():
            try:
                with open(src, "rb") as fp:
                    src = fp.read()
            except OSError as exc:
                logger.warning("Cannot read %s: %s", src, exc)
                return

        if isinstance(src, (bytes, bytearray)):
            src = io.BytesIO(cast(bytes, src))

        # ── Parse lazily; fail soft on corruption ─────────────────────
        with suppress(
            PDFSyntaxError,
            PDFPasswordIncorrect,
            PDFTextExtractionNotAllowed,
            ValueError,  # truncated or zero-byte files
            TypeError,  # non-bytes input routed here by mistake
        ):
            page_iter = extract_pages(src)

            for page_no, page in enumerate(page_iter, start=1):
                for obj in page:
                    if isinstance(obj, LTTextContainer):
                        text = obj.get_text().strip()
                        if not text:
                            continue

                        x0, y0, x1, y1 = obj.bbox
                        yield {
                            "page": page_no,
                            "type": "NarrativeText",
                            "text": text,
                            "coords": (x0, y0, x1, y1),
                        }

        logger.debug("Finished streaming pages from %r", src)


__all__: list[str] = ["PDFMinerExtractor"]
