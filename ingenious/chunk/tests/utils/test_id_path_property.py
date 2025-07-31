# ingenious/chunk/tests/utils/test_id_path_property.py
from hypothesis import given, strategies as st
from pathlib import Path
from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.utils.id_path import _norm_source


@given(path=st.builds(lambda s: Path("/", *s.split("/")), st.text(min_size=1)))
def test_hash_mode_length(path):
    cfg = ChunkConfig(id_path_mode="hash")
    out = _norm_source(path, cfg)
    assert len(out) == 12
