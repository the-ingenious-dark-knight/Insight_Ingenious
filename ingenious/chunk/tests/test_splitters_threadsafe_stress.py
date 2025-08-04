"""
Heavy‑load thread‑safety check for build_splitter.

Spawns 2 000 parallel calls to ensure that the global lock prevents
deque interleaving and that every thread gets a **unique** splitter.
"""

import concurrent.futures
from unittest.mock import MagicMock, patch

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


# Fake embedder to avoid network I/O in the semantic strategy
def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda txts: [[0.0] * 5 for _ in txts]
    return stub


@patch(
    "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
    return_value=_fake_embedder(),
)
def test_splitters_threadsafe_stress(_patched):
    STRATEGIES = ["recursive", "markdown", "token", "semantic"]

    def _task(idx: int):
        strat = STRATEGIES[idx % len(STRATEGIES)]
        cfg = ChunkConfig(strategy=strat, chunk_size=64, chunk_overlap=8)
        splitter = build_splitter(cfg)
        chunks = splitter.split_text("abc " * 50)
        return id(splitter), len(chunks)

    NUM_TASKS = 2_000
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(_task, range(NUM_TASKS)))

    # 1️⃣ all tasks succeeded and produced chunks
    assert all(count > 0 for _, count in results)

    # 2️⃣ every splitter instance id is unique – proves no accidental sharing
    ids = [sid for sid, _ in results]
    assert len(ids) == len(set(ids)), "splitter instances were shared across threads"
