"""
ingenious.chunk.tests.cli.test_cli_id_path_mode
==============================================

End‑to‑end CLI tests that exercise the three **id‑path modes** implemented by
:pyfunc:`ingenious.chunk.utils.id_path._norm_source`.

* ``rel``  – relative path when the source file is **inside** ``id_base``
             **or** the current working directory (CWD); otherwise a
             **truncated SHA‑256 digest** of the absolute path
             *(defaults to **16‑hex chars / 64 bits**, but honouring
             ``ChunkConfig.id_hash_bits``)*.
* ``hash`` – **always** a truncated digest (same length rule; salted with
             ``id_base`` when given).
* ``abs``  – normalised **absolute** POSIX path (no hashing).

The tests spawn the *real* Typer application via
:pyclass:`typer.testing.CliRunner` so they cover **argument parsing, config
validation, and writer behaviour**—equivalent to running the command from a
shell.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import jsonlines
from typer.testing import CliRunner

from ingenious.chunk.cli import cli
from ingenious.chunk.config import ChunkConfig  # ← for dynamic hash‑length

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
# Hash prefix length expected by *default* configuration
HEX_LEN = ChunkConfig().id_hash_bits // 4  # e.g. 64 bits → 16 hex

HEX_CHARS = set("0123456789abcdef")  # quick membership test


# --------------------------------------------------------------------------- #
# Helper – one‑shot execution of the CLI                                      #
# --------------------------------------------------------------------------- #
def _run_once(src: Path, mode: str, base: str | None, out: Path) -> str:
    """
    Invoke ``ingen chunk run`` exactly *once* and return the **path/hash
    prefix** (the part *before* ``"#"``) of the **first emitted chunk ID**.

    The helper keeps the test cases concise by performing all boiler‑plate:
    CLI invocation, exit‑code assertion, and JSONL parsing.
    """
    cmd = [
        "run",
        str(src),
        "--chunk-size",
        "12",
        "--chunk-overlap",
        "4",
        "--id-path-mode",
        mode,
        "--output",
        str(out),
    ]

    if base:
        cmd += ["--id-base", base]

    # `abs` mode requires an explicit acknowledgement flag
    if mode == "abs":
        cmd += ["--force-abs-path"]

    res = CliRunner().invoke(cli, cmd, catch_exceptions=False)
    assert res.exit_code == 0, res.output

    with jsonlines.open(out) as rdr:
        first = next(iter(rdr))
    return first["id"].split("#")[0]


# --------------------------------------------------------------------------- #
# 1. rel‑mode – digest *outside* base, path *inside* base                     #
# --------------------------------------------------------------------------- #
def test_rel_mode_stable_across_locations(tmp_path: Path, monkeypatch) -> None:
    """
    Expectations
    ------------
    1. A file **outside** ``id_base``/CWD hashes to a *HEX_LEN‑char* digest.
    2. The **same‑named** file **inside** ``id_base`` yields a human‑readable
       relative path.
    3. The two prefixes are therefore *different*.
    """
    # 1️⃣ Outside CWD → digest
    src = tmp_path / "alpha.txt"
    src.write_text("lorem ipsum")
    pref_outside = _run_once(src, "rel", None, tmp_path / "out1.jsonl")

    assert len(pref_outside) == HEX_LEN
    assert set(pref_outside) <= HEX_CHARS

    # 2️⃣ Inside a repo root → relative path
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / src.name).write_text("lorem ipsum")
    monkeypatch.chdir(repo)  # CWD ← repo

    pref_inside = _run_once(repo / src.name, "rel", None, tmp_path / "out2.jsonl")

    assert pref_inside == "alpha.txt"
    assert pref_inside != pref_outside


# --------------------------------------------------------------------------- #
# 2. rel‑mode – identically‑named files must hash to *different* digests      #
# --------------------------------------------------------------------------- #
def test_rel_mode_hash_uniqueness(tmp_path: Path) -> None:
    """
    Two files called ``dup.txt`` in different directories that are **both**
    outside ``id_base`` must hash to *distinct* digests of length *HEX_LEN*.
    """
    a = tmp_path / "dirA" / "dup.txt"
    b = tmp_path / "dirB" / "dup.txt"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text("foo")
    b.write_text("bar")

    id_base = tmp_path / "unrelated_base"  # ensure both are *outside*
    pref_a = _run_once(a, "rel", str(id_base), tmp_path / "o1.jsonl")
    pref_b = _run_once(b, "rel", str(id_base), tmp_path / "o2.jsonl")

    assert pref_a != pref_b
    assert len(pref_a) == len(pref_b) == HEX_LEN
    assert set(pref_a) <= HEX_CHARS and set(pref_b) <= HEX_CHARS


# --------------------------------------------------------------------------- #
# 3. hash‑mode – global uniqueness smoke‑test                                 #
# --------------------------------------------------------------------------- #
def test_hash_mode_no_collision(tmp_path: Path) -> None:
    """
    Create **50** tiny files and assert that the hash‑mode prefix is unique
    for each one.  This gives a quick regression check against accidental
    digest truncation or salt mishandling.
    """
    for i in range(50):
        (tmp_path / f"f{i}.txt").write_text("x")

    prefixes: list[str] = [
        _run_once(p, "hash", None, tmp_path / f"{p.stem}.jsonl")
        for p in tmp_path.glob("*.txt")
    ]

    dupes = [p for p, cnt in Counter(prefixes).items() if cnt > 1]
    assert not dupes, f"hash collision: {dupes!r}"
    # Optional extra guard – all prefixes must have the expected length
    assert all(len(p) == HEX_LEN for p in prefixes)


# --------------------------------------------------------------------------- #
# 4. abs‑mode – prefix equals absolute POSIX path                             #
# --------------------------------------------------------------------------- #
def test_abs_mode_contains_full_path(tmp_path: Path) -> None:
    """
    For ``id_path_mode="abs"`` the prefix is the **full absolute path** to the
    source file (converted to POSIX form).  No hashing should occur.
    """
    src = tmp_path / "zzz.txt"
    src.write_text("hello")

    pref = _run_once(src, "abs", None, tmp_path / "out.jsonl")
    assert str(src.resolve()).replace("\\", "/") == pref
