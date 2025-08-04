# ingenious/chunk/tests/utils/test_inject_overlap_metadata.py
from langchain_core.documents import Document

from ingenious.chunk.utils.overlap import inject_overlap


def test_metadata_isolated():
    """
    Mutating metadata of one overlapped chunk must not affect its siblings.
    Regression test for issue M1 (metadata aliasing).
    """
    base = Document(page_content="AAA BBB", metadata={"id": 1, "tags": ["x"]})

    c0, c1 = inject_overlap([base, base], k=3, unit="characters")

    c0.metadata["tags"].append("mutated")  # mutate in‑place
    assert c1.metadata["tags"] == ["x"]  # isolation verified
