import concurrent.futures
from unittest.mock import MagicMock, patch

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda txts: [[0.0] * 5 for _ in txts]
    return stub


@patch(
    "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
    return_value=_fake_embedder(),
)
def test_splitters_threadsafe(_):
    def _run(strategy: str):
        cfg = ChunkConfig(strategy=strategy, chunk_size=64, chunk_overlap=8)
        splitter = build_splitter(cfg)
        chunks = splitter.split_text("abc " * 100)
        return id(splitter), chunks

    strategies = ["recursive", "markdown", "token", "semantic"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        outputs = list(pool.map(_run, strategies * 8))

    # 1️⃣ no crashes & non‑empty output
    assert all(chunks for _, chunks in outputs)

    # 2️⃣ every thread received a **distinct** splitter object
    ids = [sid for sid, _ in outputs]
    assert len(ids) == len(set(ids)), "splitter instances were shared across threads"
