"""
End‑to‑end CLI tests that exercise the three **id‑path modes**:

* ``rel``  – relative path when the source file is **inside** ``id_base``  
             **or** the current working directory (CWD); otherwise a
             **12‑hex SHA‑256 digest** of the absolute path (collision‑safe).
* ``hash`` – always a 12‑hex digest (salted with ``id_base`` when given).
* ``abs``  – normalised absolute POSIX path.

The tests spawn the real Typer application via :pymeth:`typer.testing.CliRunner`
so they cover argument parsing, config‑object creation and writer
behaviour—equivalent to running the command from a shell.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import jsonlines
from typer.testing import CliRunner

from ingenious.chunk.cli import cli

# --------------------------------------------------------------------------- #
# Helper – one-shot execution                                                 #
# --------------------------------------------------------------------------- #
def _run_once(src: Path, mode: str, base: str | None, out: Path) -> str:
    """
    Invoke ``ingen chunk run`` once and return **the *prefix* of the first
    chunk ID** (everything before the ``"#"`` separator).

    Parameters
    ----------
    src : Path
        Source file passed to the CLI.
    mode : {"rel", "abs", "hash"}
        ``--id-path-mode`` value under test.
    base : str | None
        Optional ``--id-base`` argument.  ``None`` ⇒ omit flag.
    out : Path
        Destination JSONL; parent dirs are created implicitly.

    Returns
    -------
    str
        The path/hash prefix of the first emitted chunk ID.
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

    res = CliRunner().invoke(cli, cmd, catch_exceptions=False)
    assert res.exit_code == 0, res.output

    with jsonlines.open(out) as rdr:
        first = next(iter(rdr))
    return first["id"].split("#")[0]


# --------------------------------------------------------------------------- #
# 1. rel‑mode – hash *outside* base, path *inside* base                       #
# --------------------------------------------------------------------------- #
def test_rel_mode_stable_across_locations(tmp_path: Path, monkeypatch) -> None:
    """
    • When *src* is **outside** ``id_base``/CWD the prefix must be a
      12‑hex digest.  
    • The **same‑named** file **inside** ``id_base`` must use the
      human‑readable relative path.  
    • The two prefixes therefore differ.
    """
    # 1️⃣  File outside CWD  → digest
    src = tmp_path / "alpha.txt"
    src.write_text("lorem ipsum")
    out1 = tmp_path / "out1.jsonl"
    pref_outside = _run_once(src, "rel", None, out1)

    assert len(pref_outside) == 12 and all(
        c in "0123456789abcdef" for c in pref_outside
    )

    # 2️⃣  Same file copied *inside* new repo root  → readable path
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / src.name).write_text("lorem ipsum")
    monkeypatch.chdir(repo)  # CWD becomes repo

    out2 = tmp_path / "out2.jsonl"
    pref_inside = _run_once(repo / src.name, "rel", None, out2)

    assert pref_inside == "alpha.txt"
    assert pref_inside != pref_outside


# --------------------------------------------------------------------------- #
# 2. rel‑mode – two identically‑named files outside base must not collide     #
# --------------------------------------------------------------------------- #
def test_rel_mode_hash_uniqueness(tmp_path: Path) -> None:
    """
    Two files with the **same file‑name** but in different directories that
    are *both* outside ``id_base`` must hash to *different* 12‑hex digests.
    """
    a = tmp_path / "dirA" / "dup.txt"
    b = tmp_path / "dirB" / "dup.txt"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text("foo")
    b.write_text("bar")

    id_base = tmp_path / "unrelated_base"  # ensure *both* are outside base

    pref_a = _run_once(a, "rel", str(id_base), tmp_path / "o1.jsonl")
    pref_b = _run_once(b, "rel", str(id_base), tmp_path / "o2.jsonl")

    assert pref_a != pref_b
    assert len(pref_a) == len(pref_b) == 12


# --------------------------------------------------------------------------- #
# 3. hash‑mode – global uniqueness check                                      #
# --------------------------------------------------------------------------- #
def test_hash_mode_no_collision(tmp_path: Path) -> None:
    """
    Smoke‑test: 50 one‑char files hashed with default salt must all differ.
    """
    for i in range(50):
        (tmp_path / f"f{i}.txt").write_text("x")

    prefixes: list[str] = []
    for p in tmp_path.glob("*.txt"):
        prefixes.append(
            _run_once(p, "hash", None, tmp_path / f"{p.stem}.jsonl")
        )

    dupes = [v for v, c in Counter(prefixes).items() if c > 1]
    assert not dupes, f"hash collision: {dupes!r}"


# --------------------------------------------------------------------------- #
# 4. abs‑mode – must include full normalised path                             #
# --------------------------------------------------------------------------- #
def test_abs_mode_contains_full_path(tmp_path: Path) -> None:
    """
    The prefix for ``id_path_mode="abs"`` is the *absolute* POSIX path of
    the source file (no hashing).
    """
    src = tmp_path / "zzz.txt"
    src.write_text("hello")

    pref = _run_once(src, "abs", None, tmp_path / "out.jsonl")
    assert str(src.resolve()).replace("\\", "/") == pref
