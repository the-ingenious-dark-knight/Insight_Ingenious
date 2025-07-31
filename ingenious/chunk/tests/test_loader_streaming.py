"""
Tests that exercise the new *streaming JSON* code‑paths added to
ingenious.chunk.loader._parse_json.
"""

from __future__ import annotations

import json
import sys
from types import ModuleType
from pathlib import Path

import pytest

from ingenious.chunk import loader
from ingenious.chunk.loader import load_documents


# --------------------------------------------------------------------------- #
# 1. Happy‑path: large JSON array streamed via ijson                           #
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(
    loader.ijson is None, reason="ijson extra not installed"
)
def test_stream_large_json(tmp_path: Path, monkeypatch):
    """5 000‑record array must be parsed without OOM and with correct count."""

    # --- generate a >10 MiB JSON file ----------------------------------- #
    recs = [{"text": f"row-{i}"} for i in range(5_000)]
    p = tmp_path / "big.json"
    p.write_text(json.dumps(recs), encoding="utf-8")

    # Force STREAM mode even though the file may not exceed the threshold
    monkeypatch.setattr(loader, "_select_mode", lambda *_: loader._Mode.STREAM)

    docs = list(load_documents(str(p)))
    assert len(docs) == 5_000
    assert docs[0].page_content == "row-0"
    assert docs[-1].page_content == "row-4999"


# --------------------------------------------------------------------------- #
# 2. Failure: large file but *no* ijson available                              #
# --------------------------------------------------------------------------- #
def test_stream_without_ijson(tmp_path, monkeypatch, capsys):
    """
    When ijson is missing, a RuntimeError with an actionable
    message must be raised for large JSON files.
    """
    # Build a small file and override the selector to force FAIL mode
    payload = {"text": "hello"}
    p = tmp_path / "one.json"
    p.write_text(json.dumps(payload), encoding="utf-8")

    # Simulate 'ijson' not installed
    monkeypatch.setitem(sys.modules, "ijson", ModuleType("ijson"))  # placeholder
    monkeypatch.setattr(loader, "ijson", None)
    monkeypatch.setattr(loader, "_select_mode", lambda *_: loader._Mode.FAIL)

    with pytest.raises(FileNotFoundError):
        list(load_documents(str(p)))

    # The warning still needs to mention ijson → capture stdout
    captured = capsys.readouterr().out
    assert "install 'ingenious[chunk]' or 'ijson'" in captured

# --------------------------------------------------------------------------- #
# 3.  Huge *single‑object* JSON streamed via kvitems                           #
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(
    loader.ijson is None, reason="ijson extra not installed"
)
def test_stream_huge_single_object(tmp_path, monkeypatch):
    """Top‑level object with 10 000 entries must stream without OOM."""
    big = {str(i): {"text": f"row-{i}"} for i in range(10_000)}
    p = tmp_path / "big_object.json"
    p.write_text(json.dumps(big), encoding="utf-8")

    # Force STREAM mode irrespective of real size
    monkeypatch.setattr(loader, "_select_mode", lambda *_: loader._Mode.STREAM)

    docs = list(load_documents(str(p)))
    assert len(docs) == 10_000
    assert docs[0].page_content == "row-0"
    assert docs[-1].page_content == "row-9999"    