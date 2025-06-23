"""
Insight Ingenious – document-processing CLI integration tests
=============================================================

These *integration-style* smoke-tests target the public command-line
interface (CLI) shipped under the entry-point ``ingen_cli
document-processing``.  Whereas unit tests validate each internal component
in isolation, the present module verifies that those components cooperate
correctly when driven through the **highest-level user-facing surface** –
mirroring the real developer experience.

Why maintain separate integration tests?
----------------------------------------
The CLI layer glues together several loosely-coupled pieces:

* :pyfunc:`ingenious.document_processing.cli._iter_sources` – turns **file
  paths** *and* **HTTP/S URLs** into byte streams;
* Concrete *Extractor* implementations (for example, *PyMuPDF* and
  *pdfminer*);
* Rich-formatted status logging; and
* Typer-based argument parsing.

Any mis-configuration among these layers manifests first at the CLI.  A
dedicated suite therefore provides an early-warning system for regressions
and packaging errors that unit tests alone may miss.

External fixtures
-----------------
``conftest.py`` in the same package exports reusable *pytest* fixtures that
hide the mechanics of sample generation:

* ``pdf_path``  – :class:`pathlib.Path` to a minimal single-page PDF.
* ``pdf_bytes`` – Raw :class:`bytes` containing the PDF (used to stub
  network requests).

Both fixtures underpin several test modules; keeping them central avoids
duplication and guarantees consistency.

Test matrix
-----------
The suite covers six representative scenarios:

1. ``_iter_sources`` given a **single file** path.
2. ``_iter_sources`` discovering files recursively via
   :pyfunc:`pathlib.Path.rglob`.
3. ``_iter_sources`` handling an **HTTP/S URL** (network calls stubbed).
4. CLI extraction to **STDOUT** using the default engine.
5. CLI extraction to a **file** via the ``--engine`` and ``--out`` flags.
6. CLI extraction **directly from a URL**.

Each test asserts *behavioural* outcomes (exit status, presence of NDJSON
records) rather than internal state, making the suite resilient to refactors.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator
from unittest import mock

from typer.testing import CliRunner

from ingenious.document_processing.cli import _iter_sources, doc_app

__all__ = [
    # constants
    "TEST_PDF_URL",
    "cli_runner",
    # helper
    "_load_ndjson",
    # tests
    "test_iter_sources_from_file",
    "test_iter_sources_rglob",
    "test_iter_sources_url",
    "test_cli_extract_stdout",
    "test_cli_extract_to_file",
    "test_cli_extract_url_stdout",
]

# ---------------------------------------------------------------------------
# Test constants and helpers
# ---------------------------------------------------------------------------

cli_runner: CliRunner = CliRunner()
"""
Reusable Typer test runner.

Creating a single instance and sharing it across tests avoids the overhead of
spinner animations being re-initialised for every invocation under the
Rich-enabled CLI.
"""

TEST_PDF_URL: str = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)
"""
Small public PDF used for URL-oriented tests.

Selecting a stable asset prevents flakiness that might occur if the remote
server rotates, deletes, or version-locks its content.
"""


def _load_ndjson(stream: str) -> Iterator[dict]:
    """
    Yield Python dicts from an NDJSON-formatted *stream*.

    The CLI prints a Rich status line **after** emitting the NDJSON payload.
    This helper discards any line that is not valid JSON.

    Parameters
    ----------
    stream:
        Text captured from ``result.stdout``.

    Yields
    ------
    dict
        Parsed JSON objects representing individual *Element* instances
        produced by a *DocumentExtractor*.

    Notes
    -----
    Schema validation happens elsewhere; here we only ensure that
    syntactically-correct JSON objects are returned so higher-level tests can
    perform simple field checks.
    """
    for line in stream.strip().splitlines():
        line = line.strip()
        if line.startswith("{"):
            yield json.loads(line)


# ---------------------------------------------------------------------------
# _iter_sources helpers
# ---------------------------------------------------------------------------


def test_iter_sources_from_file(pdf_path: Path) -> None:
    """
    ``_iter_sources`` should yield exactly one ``(label, Path)`` tuple when
    given a *file* path.

    Assertions
    ----------
    * **Label** – must equal the original path (string form).
    * **Source** – must be the :class:`pathlib.Path` instance supplied.
    """
    label, src = next(_iter_sources(pdf_path))

    assert Path(label) == pdf_path, "Label should be the original path"
    assert src == pdf_path, "Source should be returned as a Path object"


def test_iter_sources_rglob(tmp_path: Path, pdf_path: Path) -> None:
    """
    ``_iter_sources`` should discover nested files via
    :pyfunc:`pathlib.Path.rglob`.

    Workflow
    --------
    1. Create ``tmp_path / 'nested' / <file>``.
    2. Call ``_iter_sources`` on the *parent* directory.
    3. Confirm the nested PDF appears in the yielded labels.
    """
    nested = tmp_path / "nested"
    nested.mkdir()
    dst = nested / pdf_path.name
    dst.write_bytes(pdf_path.read_bytes())

    labels = [l for l, _ in _iter_sources(tmp_path)]
    assert str(dst) in labels, "Nested PDF should be discovered by rglob"


def test_iter_sources_url(monkeypatch, pdf_bytes: bytes) -> None:
    """
    ``_iter_sources`` should return raw :class:`bytes` when passed a URL.

    The test **stubs** the network request to avoid outbound traffic by
    monkey-patching :pyfunc:`requests.get`.

    Steps
    -----
    1. Replace ``requests.get`` with a minimal stub that supplies *pdf_bytes*.
    2. Call ``_iter_sources`` with :data:`TEST_PDF_URL`.
    3. Assert that the source is ``bytes`` and the label unchanged.
    """

    class _FakeResp:  # simple stub; no pragma required
        content: bytes = pdf_bytes

        def raise_for_status(self) -> None:  # noqa: D401 – simple verb
            ...

    with mock.patch(
        "ingenious.document_processing.cli.requests.get",
        return_value=_FakeResp(),
    ):
        label, src = next(_iter_sources(TEST_PDF_URL))

    assert label.startswith("http"), "Label must be the original URL"
    assert isinstance(src, bytes), "Source should be raw bytes"


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------


def test_cli_extract_stdout(pdf_path: Path) -> None:
    """
    Default engine, default sink (STDOUT).

    Validates
    ---------
    * Exit status is zero.
    * At least one NDJSON record is emitted.
    * Each record contains a ``text`` field – full schema checks reside in
      extractor-specific unit tests.
    """
    result = cli_runner.invoke(doc_app, [str(pdf_path)])

    assert result.exit_code == 0, result.output

    payloads = list(_load_ndjson(result.stdout))
    assert payloads, "At least one NDJSON record expected"
    assert "text" in payloads[0], "Extractor should emit a 'text' field"


def test_cli_extract_to_file(tmp_path: Path, pdf_path: Path) -> None:
    """
    Explicit engine with ``--out`` flag should write NDJSON to *out* file.

    Criteria
    --------
    * Exit status must be zero.
    * Output file must exist and have non-zero size.
    """
    out = tmp_path / "out.ndjson"
    result = cli_runner.invoke(
        doc_app,
        [str(pdf_path), "--engine", "pymupdf", "--out", str(out)],
    )

    assert result.exit_code == 0, result.output
    assert out.is_file() and out.stat().st_size > 0, "Output file should exist"


def test_cli_extract_url_stdout() -> None:
    """
    End-to-end extraction when **URL** is supplied.

    Confirms that at least one NDJSON line appears on STDOUT and the command
    terminates successfully.
    """
    result = cli_runner.invoke(doc_app, [TEST_PDF_URL])

    assert result.exit_code == 0, result.output
    assert any(line.startswith("{") for line in result.stdout.splitlines()), (
        "NDJSON should appear on stdout"
    )
