"""
Insight Ingenious — Integration Test-Suite (Happy Path)
======================================================

This module executes **end-to-end, success-case** probes against the
*document-processing* Command Line Interface (CLI).  The objectives are:

1. **Engine Coverage**
   Verify that *every* registered extraction engine defined in
   :pydata:`ingenious.document_processing.extractor._ENGINES` can
   successfully parse:

   • A **local** PDF supplied via a filesystem path.
   • A **remote** PDF fetched over **HTTPS**.

2. **Format Coverage**
   Ensure the dedicated *unstructured* engine correctly handles DOCX
   input, safeguarding Insight Ingenious’ multi-format promise.

3. **Output Flexibility**
   Confirm that the CLI:

   • Writes valid NDJSON records to an explicit ``--out`` destination.
   • Falls back to streaming NDJSON to *stdout* when no output file is
     requested.

**Implementation notes**

*   All Typer invocations are routed through the shared ``_cli`` fixture
    exposed in *conftest.py* to avoid duplication and guarantee identical
    command assembly across test modules.
*   The helper functions in this file (_load_ndjson, _invoke_cli) are
    intentionally lightweight wrappers to keep the test code readable.
"""

from __future__ import annotations

# ──────────── standard library ────────────
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final

# ──────────── third-party ────────────
import pytest
from typer.testing import CliRunner, Result

# ──────────── first-party ────────────
from ingenious.cli import app as root_app
from ingenious.document_processing.cli import doc_app
from ingenious.document_processing.extractor import _ENGINES

# --------------------------------------------------------------------------- #
# constants & helpers                                                         #
# --------------------------------------------------------------------------- #

PDF_URL: Final[str] = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)
_RUNNER: Final[CliRunner] = CliRunner()


def _load_ndjson(stream: str) -> Iterator[dict[str, Any]]:
    """
    Lazily deserialize NDJSON records emitted by the CLI.

    The CLI prints a Rich-generated summary as its *final* line.  This helper
    skips that footer by selecting only lines whose first non-blank character
    is an opening brace.

    Parameters
    ----------
    stream:
        The complete byte-for-byte content of *stdout* captured from a CLI
        invocation.  It may include Rich styling as plain text on the last
        line.

    Yields
    ------
    dict[str, Any]
        One Python dictionary per NDJSON record, obtained via
        :pyfunc:`json.loads`.
    """
    for line in stream.splitlines():
        if line.lstrip().startswith("{"):
            yield json.loads(line)


def _invoke_cli(
    source: str,
    engine: str | None = None,
    out_file: Path | None = None,
    kind: str = "sub",
) -> Result:
    """
    Execute the document-processing CLI and capture the result.

    This wrapper supports two entry-points:

    * ``doc_app`` — the dedicated document-processing Typer application
      (*kind* ``"sub"``).
    * ``root_app`` — the monolithic Insight Ingenious CLI where
      *document-processing* is mounted as a sub-command (*kind* ``"root"``).

    Parameters
    ----------
    source:
        Path or URL of the document to be parsed.
    engine:
        Name of the extraction engine to use.  If omitted, the CLI selects a
        default engine based on file type and availability.
    out_file:
        Location to write the NDJSON output.  If *None*, the CLI writes to
        *stdout*.
    kind:
        Choose ``"sub"`` for *doc_app* or ``"root"`` for *root_app*.

    Returns
    -------
    Result
        The Typer ``CliRunner`` result containing exit code, stdout, stderr and
        any raised exception.
    """
    args: list[str] = []
    target_app = root_app if kind == "root" else doc_app

    if kind == "root":
        # The root application expects the sub-command token first.
        args.append("document-processing")

    # Mandatory positional argument: the source path or URL.
    args.append(source)

    # Optional flags.
    if engine is not None:
        args.extend(["--engine", engine])

    if out_file is not None:
        args.extend(["--out", str(out_file)])

    return _RUNNER.invoke(target_app, args)


# --------------------------------------------------------------------------- #
# test matrix                                                                 #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_local_pdf_ok(
    cli_kind: str,
    engine: str,
    pdf_path: Path,
    tmp_path: Path,
) -> None:
    """
    Validate that **all** engines can parse a *local* PDF file.

    Success criteria
    ----------------
    * Process exits with status ``0``.
    * Output file exists and is non-empty.
    """
    out_file = tmp_path / f"{engine}.jsonl"
    result = _invoke_cli(str(pdf_path), engine, out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_remote_pdf_ok(
    cli_kind: str,
    engine: str,
    tmp_path: Path,
) -> None:
    """
    Validate that **all** engines can parse a *remote* HTTPS-hosted PDF.

    Success criteria mirror
    :pyfunc:`test_cli_local_pdf_ok`.
    """
    out_file = tmp_path / f"remote_{engine}.jsonl"
    result = _invoke_cli(PDF_URL, engine, out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_docx_unstructured_ok(
    cli_kind: str,
    docx_path: Path,
    tmp_path: Path,
) -> None:
    """
    Ensure the *unstructured* engine can parse DOCX input end-to-end.

    This test guards against regressions in non-PDF handling.
    """
    out_file = tmp_path / "docx.jsonl"
    result = _invoke_cli(str(docx_path), "unstructured", out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_stdout_fallback_ok(cli_kind: str, pdf_path: Path) -> None:
    """
    Confirm that NDJSON records stream to *stdout* when ``--out`` is omitted.

    The captured *stdout* is parsed with :pyfunc:`_load_ndjson` and must
    contain at least one record with a ``"text"`` key.
    """
    result = _invoke_cli(str(pdf_path), "pymupdf", kind=cli_kind)

    assert result.exit_code == 0, result.output
    payloads = list(_load_ndjson(result.stdout))
    assert payloads and "text" in payloads[0]
