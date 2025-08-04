import pytest

_SAMPLE_TXT = "The quick brown fox jumps over the lazy dog.\n" * 80
_SAMPLE_MD = "# Title\n\nParagraph\n\n## Subtitle\n\nMore text."
_SAMPLE_UNICODE = "日本語123 😀 " * 40


@pytest.fixture(scope="session")
def sample_text(tmp_path_factory):
    p = tmp_path_factory.mktemp("data for test") / "doc.txt"
    p.write_text(_SAMPLE_TXT, encoding="utf-8")
    return p


@pytest.fixture(scope="session")
def sample_md(tmp_path_factory):
    p = tmp_path_factory.mktemp("data") / "doc.md"
    p.write_text(_SAMPLE_MD, encoding="utf-8")
    return p


@pytest.fixture(scope="session")
def unicode_text():
    return _SAMPLE_UNICODE


@pytest.fixture(scope="session")
def tiny_chunks_jsonl(tmp_path_factory):
    from ingenious.chunk.config import ChunkConfig
    from ingenious.chunk.factory import build_splitter

    # Use a sample text and config matching the test
    text = "A " * 1000  # or any text that will produce multiple chunks
    cfg = ChunkConfig(strategy="token", chunk_size=20, chunk_overlap=10)
    splitter = build_splitter(cfg)
    chunks = splitter.split_text(text)

    # Write chunks to file in the expected format
    p = tmp_path_factory.mktemp("data for tiny chunks") / "tiny_chunks.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            rec = {"text": chunk, "meta": {"page": 0}}
            import json

            f.write(json.dumps(rec) + "\n")
    return p
