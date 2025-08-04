"""
ingenious.chunk.tests.strategy.test_token_overlap_exact
=======================================================

Regression‑test that the token‑based overlap injected by
UnicodeSafeTokenTextSplitter complies with both the *length* and
*equality‑of‑text* invariants for every consecutive chunk pair.

Why compare text instead of token IDs?
--------------------------------------
The cl100k_base BPE can merge a trailing space from the previous chunk with
the first glyph of the next chunk, so token IDs may differ even though the
decoded strings are identical.  The test therefore asserts on *decoded
text*, allowing up to **+2 leading tokens** in the head slice—the same
tolerance used elsewhere in the suite.
"""

from __future__ import annotations

from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
ENC_NAME = "cl100k_base"
ENC = get_encoding(ENC_NAME)

K = 3  # overlap window (tokens)
EMOJI = "👩‍💻"  # multi‑code‑point (grapheme‑safe path)
TEXT = (EMOJI + " word ") * 40  # long enough to create many chunks


# --------------------------------------------------------------------------- #
# Test case                                                                   #
# --------------------------------------------------------------------------- #
def test_token_overlap_exact() -> None:
    """
    Invariant for every pair *(chunks[i‑1], chunks[i])*:

    1. ``len(tail_ids) == len(head_ids) == K``
    2. Decoded *text* of the tail appears at the start of the head
       (ignoring a possible leading space in the head segment).
    """
    cfg = ChunkConfig(
        strategy="token",
        chunk_size=30,  # small to guarantee ≥ 2 chunks
        chunk_overlap=K,
        overlap_unit="tokens",
        encoding_name=ENC_NAME,
    )
    chunks = build_splitter(cfg).split_text(TEXT)

    assert len(chunks) >= 2, "splitter produced < 2 chunks – test invalid"

    for prev, curr in zip(chunks, chunks[1:]):
        # ----------------------- length check ---------------------------- #
        prev_tail_ids = ENC.encode(prev)[-K:]
        curr_head_ids = ENC.encode(curr)[:K]
        assert len(prev_tail_ids) == len(curr_head_ids) == K

        # ------------------- semantic equality check --------------------- #
        prev_tail_text = ENC.decode(prev_tail_ids)

        # Head slice: allow +2 extra tokens to absorb BPE space‑merges
        head_ids = ENC.encode(curr)[: K + 2]
        head_text = ENC.decode(head_ids).lstrip()

        assert head_text.startswith(prev_tail_text.lstrip()), "overlap text mismatch"
