"""
ingenious.chunk.tests.utils.test_id_path_property
=================================================

Property‑based test for the **hash‑mode** branch of
`ingenious.chunk.utils.id_path._norm_source`.

The original test used a hard‑coded **12‑character** expectation that
matched the previous default of **48 bits** (12 hex digits).
Since the default has been raised to **64 bits** (16 hex digits) we now
derive the expected length directly from the runtime configuration:

    expected_len = cfg.id_hash_bits // 4

This approach stays correct if the default changes again or the caller
overrides ``id_hash_bits``.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.utils.id_path import _norm_source


# ────────────────────────────────────────────────────────────────────────────
# Hypothesis strategy
#   • Generate *absolute* POSIX‑style paths of arbitrary depth.
#     (We split a random string on "/" and pass the segments to Path.)
# ────────────────────────────────────────────────────────────────────────────
@given(
    path=st.builds(
        lambda s: Path("/", *filter(None, s.split("/"))),  # avoid empty parts
        st.text(min_size=1),
    )
)
def test_hash_mode_length(path: Path):
    """
    The hexadecimal digest produced in ``hash`` mode must be exactly
    ``id_hash_bits / 4`` characters long **and** contain only lower‑case
    hex digits (0‑9, a‑f).
    """
    cfg = ChunkConfig(id_path_mode="hash")  # uses the *default* bit length
    out = _norm_source(path, cfg)

    # Expected length in hex digits (4 bits per nibble)
    expected_len = cfg.id_hash_bits // 4

    # ── Assertions ──────────────────────────────────────────────────────
    assert len(out) == expected_len, (
        f"Digest length {len(out)} != {expected_len} (cfg.id_hash_bits={cfg.id_hash_bits})"
    )
    assert all(c in "0123456789abcdef" for c in out), "Digest is not lower‑case hex"
