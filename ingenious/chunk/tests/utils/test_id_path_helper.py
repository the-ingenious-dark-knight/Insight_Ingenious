"""
ingenious.chunk.tests.utils.test_id_path_helper
==============================================

This test‑module verifies that **_norm_source** correctly normalises source
paths under the three *id‑path* modes:

* ``abs``   – absolute POSIX path
* ``rel``   – relative path when inside *id_base* / CWD, salted hash otherwise
* ``hash``  – always a salted hash digest

The upstream default digest length was just increased from **48 bits**
(12 hex chars) to **64 bits** (16 hex chars) to reduce birthday‑collision
probabilities (see PR issue M‑4).  All assertions that previously hard‑coded
`len(...) == 12` now derive the expected hexadecimal length dynamically from
``cfg.id_hash_bits // 4`` so the tests remain robust even if the default
changes again in the future or the caller provides an explicit override.
"""

from __future__ import annotations

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.utils.id_path import _norm_source

# --------------------------------------------------------------------------- #
# Helper – common expectations                                               #
# --------------------------------------------------------------------------- #
_HEX = set("0123456789abcdef")


def _is_hex(s: str) -> bool:
    """True iff *s* consists solely of lower‑case hexadecimal digits."""
    return set(s) <= _HEX


# --------------------------------------------------------------------------- #
# 1. abs‑mode – must round‑trip the absolute path verbatim                    #
# --------------------------------------------------------------------------- #
def test_abs_mode(tmp_path):
    src = tmp_path / "foo.txt"
    cfg = ChunkConfig(id_path_mode="abs")

    assert _norm_source(src, cfg) == src.resolve().as_posix()


# --------------------------------------------------------------------------- #
# 2. rel‑mode – default *id_base* is CWD                                      #
# --------------------------------------------------------------------------- #
def test_rel_mode_default_base(tmp_path, monkeypatch):
    """
    When *src* is **inside** the current working directory the function must
    return a **readable relative path** rather than a hash digest.
    """
    src = tmp_path / "bar.txt"

    # Simulate running the CLI from the project root (parent of tmp_path)
    monkeypatch.chdir(tmp_path.parent)  # Path.cwd() ← parent directory

    cfg = ChunkConfig(id_path_mode="rel")

    assert _norm_source(src, cfg) == f"{tmp_path.name}/bar.txt"


# --------------------------------------------------------------------------- #
# 3. rel‑mode – custom id_base                                               #
# --------------------------------------------------------------------------- #
def test_rel_mode_custom_base(tmp_path):
    """
    If *src* is under a *custom* ``id_base``, the returned path must be
    expressed *relative* to that base.
    """
    base = tmp_path / "project"
    base.mkdir()

    src = base / "data" / "doc.md"
    src.parent.mkdir()  # create 'data/'

    cfg = ChunkConfig(id_path_mode="rel", id_base=base)

    assert _norm_source(src, cfg) == "data/doc.md"


# --------------------------------------------------------------------------- #
# 4. hash‑mode – always a salted digest                                      #
# --------------------------------------------------------------------------- #
def test_hash_mode(tmp_path):
    """
    ``id_path_mode="hash"`` should yield a hex digest whose length equals
    ``id_hash_bits // 4`` (because 1 hex digit = 4 bits).
    """
    src = tmp_path / "secret.txt"
    cfg = ChunkConfig(id_path_mode="hash")

    out = _norm_source(src, cfg)

    expected_len = cfg.id_hash_bits // 4
    assert len(out) == expected_len
    assert _is_hex(out)


# --------------------------------------------------------------------------- #
# 5. rel‑mode – two same‑name files outside *id_base* must not collide        #
# --------------------------------------------------------------------------- #
def test_rel_mode_hash_on_outside_base(tmp_path):
    """
    Two identically‑named files that are **both** outside ``id_base`` must
    hash to *different* digests of the correct length.
    """
    # Prepare two directories, each containing a file called 'dup.txt'
    src1 = tmp_path / "dirA" / "dup.txt"
    src2 = tmp_path / "dirB" / "dup.txt"
    src1.parent.mkdir()
    src2.parent.mkdir()
    src1.write_text("a")
    src2.write_text("b")

    cfg = ChunkConfig(id_path_mode="rel", id_base=tmp_path / "dirC")  # unrelated base
    h1 = _norm_source(src1, cfg)
    h2 = _norm_source(src2, cfg)

    expected_len = cfg.id_hash_bits // 4

    # The digests must differ and respect the expected size/charset
    assert h1 != h2
    assert len(h1) == len(h2) == expected_len
    assert _is_hex(h1) and _is_hex(h2)
