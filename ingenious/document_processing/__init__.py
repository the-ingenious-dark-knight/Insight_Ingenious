"""Insight Ingenious – ``ingenious.document_processing`` package bootstrap
=======================================================================
Centralise public access to the **document‑processing** subsystem.

The :pymod:`ingenious.document_processing` package bundles multiple extractor
engines (PDF, DOCX, plain‑text, web pages, etc.) behind a cohesive, uniform
API that emits a *lazy* stream of element dictionaries.  For **95 %** of use
cases callers simply want to *get some text out* of an arbitrary file or byte
stream – nothing more.  Importing individual engines therefore creates
unnecessary cognitive overhead.

This ``__init__.py`` solves that ergonomically by **re‑exporting** a single
function, :pydata:`extract`, that delegates all heavy‑lifting to
:pyfunc:`ingenious.document_processing.extractor.extract` while hiding the
internal module hierarchy.

Why a re‑export rather than ``from … import extract`` in user code?
------------------------------------------------------------------
* **Discoverability** – IDEs offer the helper immediately after typing
  ``document_processing.``.
* **Decoupling** – Call‑sites stay blissfully ignorant of the extractor module
  layout.  Engines can be overhauled or swapped without triggering a
  *mass‑rename* downstream.
* **Lazy import** – The underlying module is fetched via
  :pyfunc:`importlib.import_module` *at import time*, so importing
  :pymod:`ingenious.document_processing` does **not** pull in heavyweight
  dependencies like *PyMuPDF* or *python‑pptx* unless actually required.

Examples
~~~~~~~~
```python
from pathlib import Path
from ingenious.document_processing import extract

# 1️⃣  From a file‑system path (any supported format)
blocks = list(extract(Path("invoice.pdf")))

# 2️⃣  From an in‑memory byte stream (e.g. uploaded via FastAPI)
with open("report.docx", "rb") as fp:
    blocks = list(extract(fp.read()))

# 3️⃣  Streaming usage (memory‑efficient)
for block in extract("contract.pdf"):
    print(block["text"].strip())
```

Attribute summary
~~~~~~~~~~~~~~~~~
extract : Callable\[..., Iterable[dict[str, Any]]]
    **Factory‑dispatcher** that selects the appropriate extractor engine based
    on the *input type* and *content sniffing*.  Its full signature, return
    schema, and error semantics are documented where it is originally
defined.

Notes
~~~~~
* The alias retains the *callable’s* original :pyattr:`__doc__` string, so help
  utilities like :pyfunc:`help` or `pydoc` continue to show the authoritative
  documentation.
* ``__all__`` is intentionally limited to a single symbol, signalling a
  *stable* public surface.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, Callable, Iterable

# ---------------------------------------------------------------------------
# Public re‑export (lazy)
# ---------------------------------------------------------------------------

extract: Callable[..., Iterable[dict[str, Any]]] = getattr(  # type: ignore[index]
    import_module("ingenious.document_processing.extractor"),
    "extract",
)

__all__: list[str] = ["extract"]
