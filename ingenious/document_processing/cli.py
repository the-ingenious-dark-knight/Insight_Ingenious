"""Insight Ingenious – Document‑processing CLI
===========================================
Entry‑point for **command‑line** interaction with the document‑processing
sub‑system.  The module registers a :pydata:`~typer.Typer` application
(:pydata:`doc_app`) that forwards user input to the high‑level extractor helper
:pyfunc:`ingenious.document_processing.extractor.extract`.

Quick start
-----------
Run the extractor against a local or remote source and print blocks as NDJSON::

    ingen_cli document-processing extract <SOURCE> [--engine pymupdf] [--out out.jsonl]

Where *SOURCE* may be one of:

* Absolute or relative **file path** (PDF, DOCX, etc.).
* **Directory** – recursively processes all ``*.pdf`` files.
* **HTTP/S URL** – downloads the resource first (30‑second timeout).

Design principles
-----------------
1. **Zero‑config** – Sensible defaults allow casual users to extract a document
   with a single command.
2. **Streaming‑friendly** – Each element is written as a single NDJSON line to
   enable Unix pipeline composition and delta uploads.
3. **Backend‑agnostic** – The ``--engine`` flag maps directly to the extractor
   engine keyword, decoupling CLI usability from engine implementation.

High‑level flow
~~~~~~~~~~~~~~~
#. *User* invokes the CLI with a *path/URL* argument.
#. :pyfunc:`_iter_sources` converts that argument into a stream of
   ``(label, src)`` pairs, where *src* is suitable input for the extractor.
#. :pyfunc:`extract_cmd` iterates through every block produced by
   :pydata:`_extract`, appends a ``source`` annotation, and writes the element
   to the NDJSON *sink*.
#. On completion, a Rich‑coloured summary is printed.

Module‑level attributes
~~~~~~~~~~~~~~~~~~~~~~~
URL_RE
    Compiled regular expression used to detect *HTTP/S* URLs.
extract
    Alias to :pyfunc:`ingenious.document_processing.extractor.extract` imported
    lazily at runtime.

Note
----
For OCR needs, use azdocint engine.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable, Tuple, Union

import requests
import typer
from rich import print as rprint

from ingenious.document_processing.extractor import extract as _extract

# ---------------------------------------------------------------------------
# Typer application
# ---------------------------------------------------------------------------

doc_app: typer.Typer = typer.Typer(
    no_args_is_help=True,
    help="Extract structured text from local or remote PDFs, DOCX documents, PNG images, and other supported files.",
)

doc_app.__doc__ = "CLI group housing document‑processing commands."

# ---------------------------------------------------------------------------
# Constants & regexes
# ---------------------------------------------------------------------------

URL_RE: re.Pattern[str] = re.compile(r"^https?://", re.I)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _iter_sources(arg: Union[str, Path]) -> Iterable[Tuple[str, Union[bytes, Path]]]:
    """Yield normalised sources derived from *arg*.

    Parameters
    ----------
    arg
        Either an *HTTP/S* URL, a single file, or a directory.

    Yields
    ------
    tuple[str, bytes | pathlib.Path]
        *label* – Human‑readable identifier used in logs and `source` metadata.

        *src* – Raw **bytes** (downloaded file) *or* a
        :pyclass:`~pathlib.Path` object.  The tuple is suitable for direct
        consumption by :pydata:`_extract`.

    Raises
    ------
    requests.HTTPError
        Propagated when a URL fetch returns a non‑2xx status code.
    """

    # Detect URL input
    if isinstance(arg, str) and URL_RE.match(arg):
        response = requests.get(arg, timeout=30)
        response.raise_for_status()
        yield arg, response.content
        return

    # Local filesystem handling
    path = Path(arg)
    if path.is_file():
        yield str(path), path
        return

    for pdf_file in path.rglob("*.pdf"):
        yield str(pdf_file), pdf_file


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


@doc_app.command("extract")
def extract_cmd(  # noqa: D401
    path: str = typer.Argument(..., help="PDF file, directory, or HTTP/S URL"),
    engine: str = typer.Option(
        "pymupdf",
        "--engine",
        "-e",
        help="Extractor backend (pymupdf, pdfminer, unstructured, …)",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Write NDJSON lines to this file instead of stdout.",
    ),
) -> None:
    """Write extraction results to *stdout* or a file in **NDJSON** format.

    One element per line is emitted to facilitate downstream streaming.  The
    original schema of each element is preserved, and a ``source`` key is
    injected to record provenance.

    Parameters
    ----------
    path
        Input resource: file, directory, or URL.
    engine
        Name of the extractor backend.
    out
        Destination file path; *None* writes to *stdout*.
    """

    sink = open(out, "w", encoding="utf‑8") if out else sys.stdout
    count = 0

    for label, src in _iter_sources(path):
        for element in _extract(src, engine=engine):
            element.setdefault("source", label)
            sink.write(json.dumps(element, ensure_ascii=False) + "\n")
            count += 1

    if sink is not sys.stdout:
        sink.close()

    target = out if out is not None else "stdout"
    rprint(f"[green]✓ wrote {count} elements → {target}[/green]")
