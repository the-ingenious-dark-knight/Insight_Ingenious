from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _reconstruct(chunks, k: int, enc_name: str) -> str:
    """Re‑assemble *chunks* by skipping the k‑token overlap window."""
    enc = get_encoding(enc_name)
    tokens = []

    for i, ch in enumerate(chunks):
        ids = enc.encode(ch)
        tokens.extend(ids if i == 0 else ids[k:])

    return enc.decode(tokens)


def test_no_duplicate_or_missing_graphemes():
    """
    Regression for issue M‑1.

    With ``chunk_size=4`` and ``chunk_overlap=3`` the old in‑place‑slice
    implementation could duplicate or drop graphemes.  The reconstructed
    text must now match the original exactly.
    """
    text = "α β γ δ ε ζ η θ ι κ λ μ"  # 13 greek letters -> plenty of chunks
    cfg = ChunkConfig(
        strategy="token",
        chunk_size=4,
        chunk_overlap=3,
        overlap_unit="tokens",  # exercises UnicodeSafeTokenTextSplitter
    )
    splitter = build_splitter(cfg)
    chunks = splitter.split_text(text)

    rebuilt = _reconstruct(chunks, cfg.chunk_overlap, cfg.encoding_name)

    # Normalise whitespace for tokenizer quirks
    def norm(s):
        return " ".join(s.split())

    assert norm(rebuilt) == norm(text)
