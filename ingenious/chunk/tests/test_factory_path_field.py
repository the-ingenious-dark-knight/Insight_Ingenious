from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

def test_factory_handles_path_field():
    cfg = ChunkConfig(id_path_mode="rel")  # validator injects Path.cwd()
    splitter = build_splitter(cfg)         # should not raise
    assert splitter is not None
