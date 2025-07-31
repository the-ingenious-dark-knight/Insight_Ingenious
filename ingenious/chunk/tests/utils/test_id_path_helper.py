# ingenious/chunk/tests/utils/test_id_path_helper.py
from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.utils.id_path import _norm_source


def test_abs_mode(tmp_path):
    src = tmp_path / "foo.txt"
    cfg = ChunkConfig(id_path_mode="abs")
    assert _norm_source(src, cfg) == src.resolve().as_posix()


def test_rel_mode_default_base(tmp_path, monkeypatch):
    src = tmp_path / "bar.txt"
    # Simulate running CLI from repo root == tmp_path.parent
    monkeypatch.chdir(tmp_path.parent)            # Path.cwd() ← parent
    cfg = ChunkConfig(id_path_mode="rel")
    assert _norm_source(src, cfg) == f"{tmp_path.name}/bar.txt"


def test_rel_mode_custom_base(tmp_path):
    base = tmp_path / "project"
    base.mkdir()
    src = base / "data" / "doc.md"
    src.parent.mkdir()
    cfg = ChunkConfig(id_path_mode="rel", id_base=base)
    expected = "data/doc.md"
    assert _norm_source(src, cfg) == expected


def test_hash_mode(tmp_path):
    src = tmp_path / "secret.txt"
    cfg = ChunkConfig(id_path_mode="hash")
    out = _norm_source(src, cfg)
    assert len(out) == 12 and all(c in "0123456789abcdef" for c in out)

# ----------------------------------------------------------------------
# New safety check – same‑name files outside id_base must hash uniquely
# ----------------------------------------------------------------------
def test_rel_mode_hash_on_outside_base(tmp_path):
    src1 = tmp_path / "dirA" / "dup.txt"
    src2 = tmp_path / "dirB" / "dup.txt"
    src1.parent.mkdir()
    src2.parent.mkdir()
    src1.write_text("a")
    src2.write_text("b")

    cfg = ChunkConfig(id_path_mode="rel", id_base=tmp_path / "dirC")  # unrelated base
    h1 = _norm_source(src1, cfg)
    h2 = _norm_source(src2, cfg)

    assert h1 != h2 and len(h1) == 12 and len(h2) == 12