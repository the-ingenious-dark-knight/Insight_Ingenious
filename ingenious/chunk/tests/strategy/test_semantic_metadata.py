"""
tests/strategy/test_semantic_metadata.py
========================================

Regression‑test for **issue M5** – previously,
``SemanticOverlapChunker.split_text`` *discarded* metadata because the helper
created ad‑hoc ``Document`` objects, stripped their metadata, and returned only
plain strings.

The current implementation offers the keyword pair
``metadata=…`` + ``return_docs=True`` to guarantee a **metadata round‑trip**.
This test proves that contract holds.

Implementation notes
--------------------
* The semantic splitter normally instantiates an ``OpenAIEmbeddings`` object,
  which in turn requires *real* credentials in ``OPENAI_API_KEY``.
  To keep the test hermetic we monkey‑patch the class with a **fake embedder**
  that returns deterministic vectors.  This mirrors the pattern used in the
  other semantic tests.
* The patch is applied via the `@patch` decorator so the stub is automatically
  reverted when the test ends.

Assertions
----------
1. Every returned chunk is a :class:`langchain_core.documents.Document`.
2. All chunk metadata dictionaries equal the one supplied by the caller.
"""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _fake_embedder() -> MagicMock:
    """
    Return a stub object that mimics the public surface of
    ``OpenAIEmbeddings`` for the two methods used by the splitter:

    * ``embed_documents`` – returns a dummy dense vector for each text.
    * ``embed_query``      – rarely hit, but included for completeness.
    """
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 8 for _ in texts]
    stub.embed_query.return_value = [0.0] * 8
    return stub


# --------------------------------------------------------------------------- #
# Test case                                                                   #
# --------------------------------------------------------------------------- #
@patch(
    "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
    return_value=_fake_embedder(),
)
def test_split_text_preserves_metadata(_patched_embed) -> None:
    """
    End‑to‑end assertion for metadata round‑trip on the *semantic* splitter.

    Steps
    -----
    1. Build a splitter with `strategy="semantic"`.
    2. Call :py:meth:`split_text` with:
       • ``metadata`` – dictionary expected to propagate unchanged.
       • ``return_docs=True`` – request ``List[Document]`` output.
    3. Verify:
       • All outputs are :class:`Document` instances.
       • Every ``Document.metadata`` equals *exactly* the original dict.
    """
    cfg = ChunkConfig(strategy="semantic", chunk_size=32, chunk_overlap=8)
    splitter = build_splitter(cfg)

    meta = {"source": "unit-test", "page": 0}
    docs: List[Document] = splitter.split_text(  # type: ignore[assignment]
        "foo bar baz qux",
        metadata=meta,
        return_docs=True,
    )

    # -------- assertions ------------------------------------------------- #
    assert docs, "Expected at least one chunk to be produced"
    assert all(isinstance(d, Document) for d in docs), "Output must be Documents"
    assert all(d.metadata == meta for d in docs), "Metadata was not preserved"
