# ingenious/chunk/tests/strategy/test_param_matrix.py
"""
Param‑surface smoke‑test: every splitter must honour the chosen overlap_unit
for a representative matrix of settings.
"""

from itertools import product
from unittest.mock import MagicMock, patch

import pytest
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

# --------------------------------------------------------------------------- #
# Test‑matrix parameters                                                      #
# --------------------------------------------------------------------------- #
_STRATEGIES = ["recursive", "markdown", "token", "semantic"]
_UNITS = ["tokens", "characters"]
_SEPARATORS = ["", "---"]  # empty ⇒ default

_fake_embed = MagicMock()
_fake_embed.embed_documents.side_effect = lambda txts: [[0.0] * 5 for _ in txts]


# --------------------------------------------------------------------------- #
# Parametrised test                                                           #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "strategy,unit,sep",
    list(product(_STRATEGIES, _UNITS, _SEPARATORS)),
)
@patch(
    "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
    return_value=_fake_embed,
)
def test_param_surface(_, strategy: str, unit: str, sep: str):
    # Skip the now-invalid combination of semantic and characters
    if strategy == "semantic" and unit == "characters":
        pytest.skip("Semantic strategy does not support character overlap unit.")

    text = "alpha --- beta --- gamma " * 20
    cfg = ChunkConfig(
        strategy=strategy,
        chunk_size=32,
        chunk_overlap=8,
        overlap_unit=unit,
        separators=sep.split("|") if sep else None,
    )

    splitter = build_splitter(cfg)
    chunks = splitter.split_text(text)

    # -- sanity ----------------------------------------------------------- #
    assert len(chunks) >= 1  # Semantic can correctly return 1 chunk

    # Only check for overlap if there is something to overlap
    if len(chunks) < 2:
        return

    k = cfg.chunk_overlap
    enc = get_encoding(cfg.encoding_name)

    # -- invariant -------------------------------------------------------- #
    for i in range(1, len(chunks)):
        if unit == "characters":
            # exact last‑k characters must re‑appear at the next head
            assert chunks[i - 1][-k:] == chunks[i][:k]
        else:  # tokens
            prev_tail = enc.decode(enc.encode(chunks[i - 1])[-k:])
            head_text = chunks[i][: len(prev_tail) + 2]  # allow space token
            assert head_text.lstrip().startswith(prev_tail.lstrip())
