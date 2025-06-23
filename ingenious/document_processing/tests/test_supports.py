"""Insight Ingenious – generic ``supports`` contract tests
=======================================================

This *pytest* module is an **executable specification** for the minimal
behaviour that every extractor engine registered in
:pyfile:`ingenious.document_processing.extractor` must provide through its
:pyfunc:`supports` predicate.

The contract guarantees that the routing layer can make reliable decisions
without needing engine‑specific knowledge:

* **Bytes acceptance** – Engines must respond *True* when handed *any* byte
  sequence.  They may later raise a parsing error, but they cannot reject the
  bytes a priori.
* **PDF path acceptance** – Engines must recognise local PDF files supplied as
  either a :class:`pathlib.Path` instance or its string form.  The shared
  fixtures ``pdf_path`` and ``pdf_bytes`` supply realistic samples.
* **Basic rejection sanity‑check** – Engines must return *False* for patently
  unsupported inputs.  At minimum they must reject a plain‑text filename with
  a non‑PDF extension (``file.txt``).  Some engines are permissive enough to
  claim support for arbitrary bytes; the tests account for that flexibility by
  falling back to the filename assertion.

Catching deviations here prevents mis‑routed documents from reaching the more
expensive extraction and parsing stages, keeping error handling predictable.
"""

from __future__ import annotations

# ──────────────── standard library ────────────────
from typing import List, Sequence

# ──────────────── third‑party ────────────────
import pytest

# ─────────────── first‑party ───────────────
from ingenious.document_processing.extractor import _ENGINES, _load

__all__: Sequence[str] = (
    "test_supports_accepts_bytes",
    "test_supports_accepts_pdf_path",
    "test_supports_rejects_non_pdf",
)

# Stable ordering guarantees deterministic param‑ids
ENGINES: List[str] = sorted(_ENGINES)

# ───────────────────── tests ─────────────────────


@pytest.mark.parametrize("engine_name", ENGINES, ids=ENGINES)
def test_supports_accepts_bytes(engine_name: str, pdf_bytes: bytes) -> None:
    """Engines must return *True* for arbitrary byte input.

    Parameters
    ----------
    engine_name
        Symbolic key of the extractor under test.
    pdf_bytes
        Raw bytes representing a real‑world PDF.

    Returns
    -------
    None
        The test passes silently or raises :class:`AssertionError` on failure.
    """
    extractor = _load(engine_name)
    assert extractor.supports(pdf_bytes) is True, (
        f"{engine_name} should accept bytes input"
    )


@pytest.mark.parametrize("engine_name", ENGINES, ids=ENGINES)
def test_supports_accepts_pdf_path(engine_name: str, pdf_path) -> None:  # noqa: D401
    """Engines must accept the same PDF provided as *Path* and *str*.

    Parameters
    ----------
    engine_name
        Symbolic key of the extractor under test.
    pdf_path
        Path to a sample PDF provided by the fixture.

    Returns
    -------
    None
        The test passes silently or raises :class:`AssertionError` on failure.
    """
    extractor = _load(engine_name)
    # Path instance
    assert extractor.supports(pdf_path) is True, (
        f"{engine_name} should accept Path input"
    )
    # String path
    assert extractor.supports(str(pdf_path)) is True, (
        f"{engine_name} should accept str path input"
    )


@pytest.mark.parametrize("engine_name", ENGINES, ids=ENGINES)
def test_supports_rejects_non_pdf(engine_name: str) -> None:
    """Engines must reject at least one obviously incorrect input.

    The arbitrarily chosen byte blob ``b"not a pdf"`` is offered first.
    If the extractor claims *True* for that blob, we still require that it
    returns *False* for a ``.txt`` filename.

    Parameters
    ----------
    engine_name
        Symbolic key of the extractor under test.

    Returns
    -------
    None
        The test passes silently or raises :class:`AssertionError` on failure.
    """
    extractor = _load(engine_name)
    arbitrary_bytes = b"not a pdf"

    # Some engines indiscriminately accept any bytes.  That is allowed as long
    # as they still reject an obviously wrong file extension.
    if extractor.supports(arbitrary_bytes):
        assert extractor.supports("file.txt") is False, (
            f"{engine_name} should reject .txt even if it accepts arbitrary bytes"
        )
        return

    assert extractor.supports("file.txt") is False, (
        f"{engine_name} should reject .txt input"
    )
