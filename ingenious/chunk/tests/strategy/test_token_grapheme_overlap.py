from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

EMOJI = "👩‍💻"  # multi‑code‑point emoji with ZWJ
TEXT = (EMOJI + " ") * 40  # long enough to force many chunks
ZWLJ = "\u200d"  # zero‑width joiner


def _assert_no_split(chunks):
    """
    Ensure no chunk *starts* or *ends* with an orphan ZWJ, a reliable signal
    that the grapheme was sliced in half.
    """
    for c in chunks:
        assert not c.startswith(ZWLJ)
        assert not c.endswith(ZWLJ)


def test_token_unit_grapheme_overlap():
    cfg = ChunkConfig(
        strategy="token",
        chunk_size=8,  # deliberately tiny
        chunk_overlap=4,
        overlap_unit="tokens",
    )
    chunks = build_splitter(cfg).split_text(TEXT)
    _assert_no_split(chunks)


def test_character_unit_grapheme_overlap():
    cfg = ChunkConfig(
        strategy="token",
        chunk_size=12,
        chunk_overlap=5,
        overlap_unit="characters",
    )
    chunks = build_splitter(cfg).split_text(TEXT)
    _assert_no_split(chunks)
