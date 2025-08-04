from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _fake_embedder():
    """A mock embedder to prevent real network calls during tests."""
    stub = MagicMock()
    # Return a list of lists (embeddings) matching the number of input texts
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 8 for _ in texts]
    return stub


def test_semantic_chunker_fails_with_invalid_percentile():
    """
    Verify that the ChunkConfig validation fails when an invalid percentile
    is provided for the semantic strategy.
    """
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 100"
    ):
        ChunkConfig(
            strategy="semantic",
            semantic_threshold_percentile=101,  # Invalid percentile
        )


@patch(
    "ingenious.chunk.strategy.langchain_semantic._select_embeddings",
    return_value=_fake_embedder(),
)
def test_semantic_chunker_succeeds_with_valid_percentile(mock_select_embeddings):
    """
    Verify that the semantic chunker initializes and runs correctly when a valid
    percentile is provided.
    """
    try:
        cfg = ChunkConfig(
            strategy="semantic",
            semantic_threshold_percentile=95,  # Valid percentile
        )
        splitter = build_splitter(cfg)
        assert splitter is not None
        # Ensure splitting does not raise an error
        splitter.split_text("This is the first sentence. This is the second sentence.")
    except ValidationError as e:
        pytest.fail(f"Initialization or splitting failed with a valid percentile: {e}")
