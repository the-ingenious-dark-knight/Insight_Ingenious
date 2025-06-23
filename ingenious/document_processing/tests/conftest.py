"""insight‑ingenious ‑ Shared *pytest* configuration
===================================================

Centralised fixtures and helpers used by the *Insight Ingenious* document‑
processing test‑suite live here.  They aim to keep the repository free of
binary artefacts while exercising the public extractor API as realistically as
possible.  The module follows the Development Guide’s recommendations for
clarity, resilience, and optional‑dependency detection.

Key design points
-----------------
* **No committed binaries** – sample PDFs are downloaded at run‑time and cached
  to ``tmp_path``.  DOCX files are generated on‑the‑fly from the extracted PDF
  text, so every extractor is tested on multiple formats without polluting
  version control.
* **Graceful network degradation** – when a remote file cannot be fetched the
  relevant tests are either *xfail* (cached copy available) or *skipped*
  (first‑time fetch).  Continuous‑integration runs therefore remain stable
  regardless of external connectivity.
* **Optional‑dependency discovery** – fixtures detect whether *PyMuPDF*,
  *python‑docx*, *pdfminer.six*, or *unstructured* are installed and adjust the
  test matrix automatically.  This lets contributors run a minimal subset of
  tests locally while the CI pipeline executes the full suite.

Every public fixture or helper comes with an exhaustive NumPy‑style docstring
that documents **Parameters**, **Returns/Yields**, and any **Raises** or
**Side‑Effects**.  The public surface is enumerated in :pydata:`__all__` so
that unused‑import linters can work effectively.
"""

from __future__ import annotations

import importlib
import importlib.util

# ──────────────── standard library ────────────────
from pathlib import Path
from typing import Final, Iterator

# ──────────────── third‑party ────────────────
import pytest
import requests

# ─────────────── first‑party ───────────────
from ingenious.document_processing import extract as _extract_docs
from ingenious.document_processing.extractor import _load

__all__ = [
    "DEFAULT_TIMEOUT",
    "fitz_mod",
    "pdf_path",
    "pdf_bytes",
    "tiny_pdf_path",
    "tiny_pdf_bytes",
    "docx_mod",
    "docx_path",
    "docx_bytes",
    "pdfminer_available",
    "unstructured_available",
    "pymupdf",
]

# ─────────────────── constants ───────────────────
DEFAULT_TIMEOUT: Final[int] = 10  # seconds

#: Two lightweight, publicly accessible PDFs hosted by DenseBreast‑Info.
PDF_URLS: list[str] = [
    "https://densebreast-info.org/wp-content/uploads/2024/06/Patient-Fact-Sheet-English061224.pdf",
    "https://densebreast-info.org/wp-content/uploads/2024/11/English_PatientBrochure_112924.pdf",
]

# ───────────── helper functions ─────────────


def _download(url: str, cache_dir: Path) -> Path:
    """Fetch *url* into *cache_dir* with caching and fault‑tolerance.

    Parameters
    ----------
    url
        Absolute URL pointing at the remote PDF to download.
    cache_dir
        Directory used to store a persistent cached copy so subsequent test
        runs do not hit the network again.

    Returns
    -------
    pathlib.Path
        Path to the cached (or freshly downloaded) file on disk.

    Side Effects
    ------------
    * Writes the downloaded content to *cache_dir*.
    * Interacts with *pytest*: marks the calling test as *xfail* when the
      download fails but a cached copy exists; otherwise skips the test.
    """
    cache_dir.mkdir(exist_ok=True)
    destination: Path = cache_dir / Path(url).name

    # Return cached copy immediately if available.
    if destination.exists():
        return destination

    # Attempt a fresh download.
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        # Fallback: cached copy available → xfail; otherwise skip.
        if destination.exists():
            pytest.xfail(reason=f"Using cached PDF after download failure: {exc}")
            return destination
        pytest.skip(reason=f"Cannot fetch {url} ({exc}); skipping network test")

    destination.write_bytes(response.content)
    return destination


# ───────────────────── fixtures ─────────────────────


@pytest.fixture(scope="session")
def fitz_mod():  # noqa: D401 – fixture name mandated by pytest
    """Import and expose the *PyMuPDF* ``fitz`` module.

    Returns
    -------
    module
        The imported ``fitz`` module.

    Notes
    -----
    The fixture calls :pyfunc:`pytest.skip` at **collection‑time** if *PyMuPDF*
    is not installed so that dependent tests are automatically excluded.
    """
    try:
        return importlib.import_module("fitz")
    except ImportError:  # pragma: no cover – environment specific
        pytest.skip("PyMuPDF not installed")


@pytest.fixture(scope="session", params=PDF_URLS, ids=lambda url: Path(url).name)
def pdf_path(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Provide each remote PDF as a **local** file path.

    Yields
    ------
    pathlib.Path
        Location of the cached PDF within a temporary directory.
    """
    cache: Path = tmp_path_factory.mktemp("pdf_cache")
    return _download(request.param, cache)


@pytest.fixture()
def pdf_bytes(pdf_path: Path) -> bytes:
    """Return the raw bytes of the currently parametrised PDF.

    Parameters
    ----------
    pdf_path
        Path supplied by the :pyfixture:`pdf_path` fixture.

    Returns
    -------
    bytes
        Binary content that some extractor APIs accept directly.
    """
    return pdf_path.read_bytes()


# ───── legacy aliases (deprecated; remove in v1.0) ─────


@pytest.fixture()
def tiny_pdf_path(pdf_path: Path) -> Path:  # noqa: D401 – fixture alias
    """Alias for :pyfixture:`pdf_path` (scheduled for removal in *v1.0*)."""
    return pdf_path


@pytest.fixture()
def tiny_pdf_bytes(pdf_bytes: bytes) -> bytes:  # noqa: D401 – fixture alias
    """Alias for :pyfixture:`pdf_bytes` (scheduled for removal in *v1.0*)."""
    return pdf_bytes


# ───────────── DOCX‑related fixtures ─────────────


@pytest.fixture(scope="session")
def docx_mod():  # noqa: D401 – fixture name mandated
    """Import and expose *python‑docx*.

    Returns
    -------
    module
        The imported ``docx`` module.

    Notes
    -----
    Skips dependent tests when *python‑docx* is not available.
    """
    try:
        return importlib.import_module("docx")
    except ImportError:  # pragma: no cover
        pytest.skip("python‑docx not installed")


def _pdf_to_text(src: Path) -> str:
    """Extract plain text from *src* using the public :pyfunc:`extract` API.

    Parameters
    ----------
    src
        Path to a PDF on disk.

    Returns
    -------
    str
        Newline‑separated text aggregated from the extractor output.  An empty
        string signals no textual content.
    """
    blocks = _extract_docs(src)
    text_lines: Iterator[str] = (block["text"] for block in blocks if block.get("text"))
    return "\n".join(text_lines).strip()


@pytest.fixture()
def docx_path(
    tmp_path: Path,
    pdf_path: Path,
    docx_mod,
):
    """Generate a DOCX mirroring the textual content of *pdf_path*.

    Parameters
    ----------
    tmp_path
        Per‑test temporary directory provided by **pytest**.
    pdf_path
        Current PDF under test, supplied by :pyfixture:`pdf_path`.
    docx_mod
        Imported ``docx`` module injected by :pyfixture:`docx_mod`.

    Returns
    -------
    pathlib.Path
        Location of the newly created DOCX file.  The file is cached within
        *tmp_path* so subsequent calls in the same test reuse the artefact.
    """
    destination: Path = tmp_path / f"{pdf_path.stem}.docx"
    if destination.exists():
        return destination

    imported_text: str = _pdf_to_text(pdf_path) or f"Empty extract from {pdf_path.name}"
    document = docx_mod.Document()
    for line in imported_text.splitlines():
        document.add_paragraph(line)
    document.save(destination)
    return destination


@pytest.fixture()
def docx_bytes(docx_path: Path) -> bytes:
    """Return the raw bytes of the generated DOCX file.

    Parameters
    ----------
    docx_path
        Path returned by the :pyfixture:`docx_path` fixture.

    Returns
    -------
    bytes
        Binary content suitable for extractor APIs that accept streams.
    """
    return docx_path.read_bytes()


# ───── optional‑dependency detectors ─────


@pytest.fixture(scope="session")
def pdfminer_available() -> bool:  # noqa: D401 – boolean return
    """Tell whether :pypi:`pdfminer.six` is importable.

    Returns
    -------
    bool
        ``True`` if the package is importable, otherwise ``False``.
    """
    return importlib.util.find_spec("pdfminer") is not None


@pytest.fixture(scope="session")
def unstructured_available() -> bool:  # noqa: D401 – boolean return
    """Tell whether :pypi:`unstructured` is importable.

    Returns
    -------
    bool
        ``True`` if the package is importable, otherwise ``False``.
    """
    return importlib.util.find_spec("unstructured") is not None


# ────────── shared extractor fixture ──────────


@pytest.fixture(scope="session")
def pymupdf():
    """Return a session‑scoped *PyMuPDF* extractor instance.

    Returns
    -------
    ingenious.document_processing.extractor.BaseExtractor
        The cached extractor object constructed via :pyfunc:`_load`.
    """
    return _load("pymupdf")
