"""Insight Ingenious – negative‑path CLI tests
=================================================
This module contains *error‑path* and *integrity* tests for the
``document-processing`` Typer sub‑command provided by
:pyfunc:`ingenious.document_processing.cli.doc_app`.  Whereas
``test_cli.py`` covers *happy‑path* scenarios, tests here deliberately push
invalid inputs or hostile environments to assert that:

1. **Unknown extractor engines** are rejected with an explicit
   :class:`ValueError` propagated by Typer.
2. **Unwritable output destinations** cause a non‑zero exit but do **not**
   crash the Python interpreter.
3. The **stdout NDJSON stream** remains syntactically valid JSON Lines even
   when no ``--out`` flag is supplied (integrity guard).

Fixtures
--------
pytest provides several fixtures (via *conftest.py*) that these tests rely on:

``pdf_path``
    :class:`pathlib.Path` to a temp sample PDF used as CLI input.
``tmp_path``
    :class:`pathlib.Path` to an isolated, writable scratch directory.

Running the suite
-----------------
Simply execute ``uv run pytest`` (as documented in the Development Guide) or
``pytest -q ingenious/document_processing/tests/test_cli_error_paths.py`` to
focus on this file.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import List

import pytest
from typer.testing import CliRunner

from ingenious.document_processing.cli import doc_app

cli_runner: CliRunner = CliRunner()

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #


def _make_unwritable_dir(base: Path) -> Path:  # noqa: D401
    """Return a directory inside *base* that the current process **cannot** write.

    The helper manipulates POSIX permission bits to strip *write* access from
    a newly‑created directory.  On Windows, permission semantics differ and
    the attempt would be unreliable, so the caller is skipped via an internal
    :pyfunc:`pytest.skip`.

    Parameters
    ----------
    base
        Parent directory (pytest's ``tmp_path`` fixture is ideal).

    Returns
    -------
    Path
        The newly‑created, unwritable directory.  This can be passed to the
        CLI ``--out`` flag to trigger an *EPERM*‑style failure.
    """
    target = base / "no_write"
    target.mkdir(exist_ok=True)

    if os.name == "nt":  # pragma: no cover – Windows
        pytest.skip("chmod‑based unwritable dir not supported on Windows")

    # Read & execute only; remove write bit for user/group/others.
    target.chmod(stat.S_IREAD | stat.S_IEXEC)
    return target


# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #


def test_cli_unknown_engine(pdf_path: Path, tmp_path: Path) -> None:
    """Supplying an unknown ``--engine`` must raise :class:`ValueError`."""
    out_file = tmp_path / "bad.jsonl"
    result = cli_runner.invoke(
        doc_app,
        [str(pdf_path), "--engine", "nope", "--out", str(out_file)],
    )

    # Typer propagates the Python exception and sets a non‑zero exit code.
    assert result.exit_code != 0, "CLI unexpectedly exited with code 0"
    assert isinstance(result.exception, ValueError), result.exception
    assert "Unknown engine" in str(result.exception)


def test_cli_unwritable_out(pdf_path: Path, tmp_path: Path) -> None:
    """CLI should abort gracefully when ``--out`` is unwritable."""
    unwritable_dir = _make_unwritable_dir(tmp_path)
    result = cli_runner.invoke(doc_app, [str(pdf_path), "--out", str(unwritable_dir)])

    assert result.exit_code != 0, "CLI did not fail as expected on unwritable --out"


def test_cli_stdout_json_integrity(pdf_path: Path) -> None:
    """Running without ``--out`` must emit *valid* NDJSON on *stdout*."""
    result = cli_runner.invoke(doc_app, [str(pdf_path)])
    assert result.exit_code == 0, result.output

    # Extract JSON Lines (skip final Rich status line).
    json_objs: List[dict] = [
        json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")
    ]
    assert json_objs, "No JSON objects found in CLI output"
    assert all("text" in obj for obj in json_objs), "Missing 'text' key in payloads"
