"""Insight Ingenious – Extractor‑registry integrity tests
=====================================================

This *pytest* module acts as a **canary** for the extractor registry declared
in :pyfile:`ingenious.document_processing.extractor`.  The registry maps short
engine keys (for example ``"pymupdf"``) to fully‑qualified import strings of
form ``"package.sub.mod:ClassName"``.  Because that mapping is consumed by
nearly every document‑processing feature, breakage here would cascade widely –
these tests therefore run early in CI to catch issues fast.

Test coverage
-------------
1. **Import sanity** – each dotted path in :pydata:`_ENGINES` *must* import and
   expose the advertised extractor class.
2. **Fail‑fast contract** – the public loader helper :pyfunc:`_load` *must*
   raise :class:`ValueError` when given an unrecognised key; silent fall‑back
   would obscure spelling mistakes and mis‑configuration.

Every callable includes an exhaustive NumPy‑style docstring to satisfy the
Development Guide’s documentation rule.
"""

from __future__ import annotations

# ────────────────── standard library ──────────────────
from importlib import import_module
from typing import Tuple

# ──────────────────── third‑party ────────────────────
import pytest

# ───────────────────── first‑party ────────────────────
from ingenious.document_processing.extractor import _ENGINES, _load

__all__: Tuple[str, ...] = (
    "test_registry_entries_importable",
    "test_load_rejects_unknown_engine",
)

# ─────────────────────── tests ────────────────────────


@pytest.mark.parametrize(
    ("engine_name", "dotted_path"),
    sorted(_ENGINES.items()),
    ids=lambda item: item[0] if isinstance(item, tuple) else str(item),
)
def test_registry_entries_importable(engine_name: str, dotted_path: str) -> None:
    """Assert that the registry entry *dotted_path* can be imported.

    Parameters
    ----------
    engine_name
        The symbolic key clients use to request the extractor (for example
        ``"pymupdf"``).
    dotted_path
        Import specification in the format ``"some.mod.path:ClassName"``.

    Returns
    -------
    None
        The test passes silently when the module imports and the attribute is
        present – otherwise :class:`AssertionError` is raised.

    Raises
    ------
    AssertionError
        If the target module cannot be imported **or** the expected class is
        missing, making the registry entry invalid.
    """
    module_path, class_name = dotted_path.split(":", maxsplit=1)
    module = import_module(module_path)

    assert hasattr(module, class_name), (
        f"{engine_name}: expected {class_name} inside {module_path}, "
        "but it could not be found"
    )


def test_load_rejects_unknown_engine() -> None:
    """Ensure :pyfunc:`_load` raises :class:`ValueError` for bad keys.

    The helper *must* fail loudly rather than returning *None* or a default –
    this protects callers from silent configuration mistakes.

    Returns
    -------
    None
        The test passes when the expected exception is raised.
    """
    with pytest.raises(ValueError):
        _load("definitely‑does‑not‑exist")
