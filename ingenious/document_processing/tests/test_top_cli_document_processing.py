"""
Insight Ingenious – end-to-end CLI smoke-tests
==============================================

This module executes a **minimal-viable end-to-end check** for the public
command-line interface exposed via ::

    ingen_cli document-processing ...

The goal is *confidence over coverage*: prove that the CLI wire-up still works
after any change to Typer options, extractor registration, or stream handling.
A single failure here flags the entire CLI pipeline as broken long before
deeper unit- or integration-level assertions run.

Why another test layer?
-----------------------
``tests/unit`` validates extractor internals in isolation and
``tests/integration`` uses stubs or monkey-patches to verify high-level logic
without external I/O.  These **smoke-tests** purposely keep disk and network
I/O *alive* to catch:

* Missing dynamic libraries (e.g. PyMuPDF, pdfminer)
* Bad registry keys in :data:`ingenious.document_processing.extractor._ENGINES`
* Packaging errors that prevent Typer from bootstrapping
* Broken Rich/NDJSON interleave on stdout

Test matrix
-----------
===============  ==============================  ======================================
ID               Scenario                        Engines exercised
===============  ==============================  ======================================
①                Local sample PDF               *all* values in ``_ENGINES``
②                Remote PDF (HTTP download)     *all* values in ``_ENGINES``
③                Local DOCX                     ``unstructured`` (only engine with DOCX)
④                Stdout fallback (no ``--out``) ``pymupdf`` (default engine)
===============  ==============================  ======================================

*All* scenarios assert an **exit-code of 0** *and* at least one NDJSON record.
If either condition fails, CI surfaces the defect immediately.
"""

from __future__ import annotations

# ──────────── standard library ────────────
from pathlib import Path
from typing import List

# ──────────── third-party ────────────
import pytest
from typer.testing import CliRunner, Result

# ──────────── first-party ────────────
from ingenious.cli import app as root_app
from ingenious.document_processing.extractor import _ENGINES

__all__: List[str] = [
    "_cli",
    "test_cli_local_pdf_all_engines",
    "test_cli_remote_pdf_all_engines",
    "test_cli_local_docx_unstructured",
    "test_cli_local_pdf_default_stdout",
]

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

runner: CliRunner = CliRunner()
runner.__doc__ = (
    "Shared Typer test runner reused by every test case to avoid repeatedly "
    "initialising Rich's progress spinner and console rendering pipeline."
)

REMOTE_PDF_URL: str = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)

# Stable single-page PDF (~100 kB) hosted by densebreast-info.org.
# Chosen for quick transfers and long-lived availability; used by all
# network-enabled smoke-tests.
REMOTE_PDF_URL: str = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #


def _cli(source: str, engine: str, out_file: Path | None = None) -> Result:
    """
    Run ``ingen_cli document-processing`` synchronously and capture its output.

    Parameters
    ----------
    source:
        String path or URL pointing to the asset under test.  Local paths are
        forwarded verbatim; HTTP(S) URLs trigger an internal download via
        ``requests``.
    engine:
        Name of the extractor backend, exactly as stored in
        :data:`ingenious.document_processing.extractor._ENGINES`.
    out_file:
        Optional :class:`pathlib.Path` where NDJSON should be written.  When
        ``None`` the CLI writes to **stdout**, which is useful for validating
        pipeline behaviour in a Unix shell.

    Returns
    -------
    typer.testing.Result
        Captured execution artefacts: numeric ``exit_code`` plus text
        ``stdout`` and ``stderr``.

    Notes
    -----
    * The helper builds the argument vector in one place so that individual
      tests remain declarative.
    * It intentionally *does not* catch or re-raise exceptions—any unexpected
      stack trace should fail the calling test directly.
    """
    args: List[str] = ["document-processing", source, "--engine", engine]
    if out_file is not None:
        args.extend(["--out", str(out_file)])

    return runner.invoke(root_app, args)


# --------------------------------------------------------------------------- #
# Matrix ① – local PDF parsed by *every* engine
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_local_pdf_all_engines(
    engine: str,
    pdf_path: Path,
    tmp_path: Path,
) -> None:
    """
    End-to-end parse of *pdf_path* using each registered extractor.

    Parameters
    ----------
    engine:
        Parametrised fixture value supplied by *pytest* – one per registry key.
    pdf_path:
        Fixture pointing to a tiny sample PDF bundled with the repository.
    tmp_path:
        Unique temporary directory created by *pytest*.

    Asserts
    -------
    * Exit-code is zero.
    * File *out* exists and its size is > 0 bytes (non-empty NDJSON).
    """
    out: Path = tmp_path / f"{engine}.jsonl"
    result: Result = _cli(str(pdf_path), engine, out)

    assert result.exit_code == 0, result.output
    assert out.is_file() and out.stat().st_size > 0


# --------------------------------------------------------------------------- #
# Matrix ② – remote PDF parsed by *every* engine
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_remote_pdf_all_engines(
    engine: str,
    tmp_path: Path,
) -> None:
    """
    Fetch **REMOTE_PDF_URL** over HTTPS and pipe it into each extractor.

    Parameters
    ----------
    engine:
        One of the registry keys enumerated from ``_ENGINES``.
    tmp_path:
        Per-test temporary directory for output files.

    The test ensures that the extractor’s ``bytes`` ingestion path works and
    that transient network hiccups surface as test failures.
    """
    out: Path = tmp_path / f"remote_{engine}.jsonl"
    result: Result = _cli(REMOTE_PDF_URL, engine, out)

    assert result.exit_code == 0, result.output
    assert out.is_file() and out.stat().st_size > 0


# --------------------------------------------------------------------------- #
# Scenario ③ – DOCX via *unstructured*
# --------------------------------------------------------------------------- #


def test_cli_local_docx_unstructured(docx_path: Path, tmp_path: Path) -> None:
    """
    Exercise the *unstructured* backend’s DOCX parser on a local file.

    Parameters
    ----------
    docx_path:
        Fixture that returns a minimal DOCX test asset.
    tmp_path:
        Temporary directory unique to this test invocation.

    Both assertions match the PDF cases: zero exit-code and non-empty NDJSON.
    """
    out: Path = tmp_path / "docx.jsonl"
    result: Result = _cli(str(docx_path), "unstructured", out)

    assert result.exit_code == 0, result.output
    assert out.is_file() and out.stat().st_size > 0


# --------------------------------------------------------------------------- #
# Scenario ④ – stdout fallback
# --------------------------------------------------------------------------- #


def test_cli_local_pdf_default_stdout(pdf_path: Path) -> None:
    """
    Validate the default **stdout** sink when the user omits ``--out``.

    Parameters
    ----------
    pdf_path:
        Fixture providing the local sample PDF.

    The stream contains two kinds of lines:

    1. NDJSON rows – each must start with ``"{"`` so downstream tools like
       ``jq`` can parse them.
    2. A single Rich status line – ignored by the assertion below.

    Pass criteria
    -------------
    * Exit-code ``0``.
    * At least one NDJSON row detected on stdout.
    """
    result: Result = _cli(str(pdf_path), "pymupdf")

    assert result.exit_code == 0, result.output
    assert any(line.lstrip().startswith("{") for line in result.stdout.splitlines()), (
        "No JSON object detected on stdout – extractor likely failed"
    )
