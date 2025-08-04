# ingenious/chunk/tests/strategy/test_encoding_override.py
"""
Regression‑test for issue M‑7 – ensure that supplying a custom
``encoding_name`` honours the token budget for **every** splitter
strategy that supports token‑level budgets.
"""

from __future__ import annotations

from itertools import product
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

# --------------------------------------------------------------------------- #
# Test‑matrix parameters                                                      #
# --------------------------------------------------------------------------- #
ENCODINGS: List[str] = ["p50k_base", "r50k_base"]  # non‑default
STRATEGIES: List[str] = ["recursive", "markdown", "token", "semantic"]

TEXT = "alpha beta gamma delta " * 200  # large enough to force splits
CHUNK_SIZE = 32
OVERLAP = 8
MAX_ALLOWED = CHUNK_SIZE + 2 * OVERLAP  # after overlap injection


def _fake_embedder():
    """Stub that returns deterministic vectors – avoids real network calls."""
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda txts: [[0.0] * 5 for _ in txts]
    return stub


# --------------------------------------------------------------------------- #
# Parametrised test                                                           #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("enc_name,strategy", product(ENCODINGS, STRATEGIES))
@patch(
    "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
    return_value=_fake_embedder(),
)
@patch(
    "ingenious.chunk.strategy.langchain_semantic.AzureOpenAIEmbeddings",
    return_value=_fake_embedder(),
)
def test_encoding_override_budget(_, __, enc_name: str, strategy: str) -> None:
    """
    Every chunk produced with *enc_name* must stay within the relaxed token
    budget (CHUNK_SIZE + 2 × OVERLAP). This does not apply to the semantic
    strategy, which sizes chunks based on topic, not token count.
    """
    cfg = ChunkConfig(
        strategy=strategy,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=OVERLAP,
        encoding_name=enc_name,
    )
    splitter = build_splitter(cfg)

    chunks = splitter.split_text(TEXT)
    assert chunks, "splitter produced no chunks – test invalid"

    # The semantic strategy intentionally ignores chunk_size for sizing,
    # so we skip the budget assertion for it.
    if strategy == "semantic":
        return

    enc = get_encoding(enc_name)
    assert all(
        len(enc.encode(c if isinstance(c, str) else c.page_content)) <= MAX_ALLOWED
        for c in chunks
    ), f"{strategy}/{enc_name} emitted over‑budget chunk"
