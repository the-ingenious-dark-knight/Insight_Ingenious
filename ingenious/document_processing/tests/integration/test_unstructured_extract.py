"""
Insight Ingenious – *Unstructured* extractor integration tests
=============================================================

This module belongs to the **integration** tier of the
``ingenious.document_processing`` test-suite.  It validates the adaptor that
leverages the `unstructured` library to parse multiple office-style formats
(*PDF*, *DOCX*, *PPTX*).

Validation scope
----------------
1. **Smoke extraction**
   For every supported format and input variant (disk *path* and in-memory
   *bytes*) the extractor must emit at least one element, each conforming to a
   minimal schema.  A second invocation with identical input must return an
   *identical* list, proving determinism.

2. **Coordinate serialisation**
   The private helper
   :pyfunc:`ingenious.document_processing.extractor.UnstructuredExtractor._coords_to_jsonable`
   must convert the eclectic coordinate objects returned by *unstructured*
   into JSON-serialisable primitives without raising.

3. **Format support probes**
   :pyfunc:`ingenious.document_processing.extractor.DocumentExtractor.supports`
   must return the correct boolean for known and unknown suffixes, while
   :pyfunc:`extract` must silently return an empty iterator for unsupported
   files.
"""

from __future__ import annotations

# ──────────────── standard library ────────────────
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

# ──────────────── third-party ────────────────
import pytest

# ─────────────── first-party ───────────────
from ingenious.document_processing.extractor import _load

# ─────────────────── constants ───────────────────
_TEXT_REQUIRED_TYPES: set[str] = {"narrativetext", "paragraph", "title", "head"}

_HEADERS: dict[str, bytes] = {
    ".pdf": b"%PDF-1.7\n",
    ".docx": b"PK\x03\x04",  # ZIP header – sufficient for a DOCX smoke probe
    ".pptx": b"PK\x03\x04",
}


# ───────────── helper functions ─────────────
def _assert_valid_element(el: dict[str, Any]) -> None:
    """
    Perform a *minimal* schema validation on an element dictionary.

    Mandatory keys
    --------------
    ``page``   ``int >= 1`` for PDFs, or ``None`` for DOCX/PPTX
    ``type``   Non-empty ``str``
    ``text``   ``str`` (may be empty for non-textual elements)

    Additional rule
    ---------------
    If ``type`` is one of *NarrativeText*, *Paragraph*, *Title* or *Head*
    (case-insensitive) the ``text`` field **must not** be empty.

    Parameters
    ----------
    el
        Element dictionary returned by the *Unstructured* extractor.

    Raises
    ------
    AssertionError
        When any structural or semantic requirement is violated.
    """
    page = el["page"]
    # For PDFs page is an integer; for DOCX/PPTX Unstructured returns None.
    assert (page is None) or (isinstance(page, int) and page >= 1), "invalid `page`"
    assert isinstance(el["type"], str) and el["type"], "empty `type`"
    assert isinstance(el["text"], str), "`text` is not a string"

    if el["type"].lower() in _TEXT_REQUIRED_TYPES:
        assert el["text"], "`text` required for narrative element"


# ──────────────────────────── fixtures ────────────────────────────
@pytest.fixture(scope="module")
def ux(unstructured_available: bool):
    """
    Module-scoped *UnstructuredExtractor* fixture.

    The extractor is initialised once per module – expensive model loading
    inside `unstructured` is therefore paid only once.

    Parameters
    ----------
    unstructured_available
        Boolean fixture (from *conftest.py*) indicating whether the dependency
        is importable.

    Returns
    -------
    ingenious.document_processing.extractor.DocumentExtractor
        Wrapper around the `unstructured` runtime.

    Notes
    -----
    If *unstructured* is unavailable the entire module is skipped.
    """
    if not unstructured_available:
        pytest.skip("unstructured not installed")
    return _load("unstructured")


@pytest.fixture
def src(request):
    """
    Resolve the *indirect* ``src`` parametrisation.

    Indirection allows a single parametrised test to consume heterogeneous
    fixtures – plain *bytes* and *Path* objects – while keeping the parameter
    table flat and readable.

    Parameters
    ----------
    request : _pytest.fixtures.FixtureRequest
        Built-in pytest object detailing the current parametrisation context.

    Returns
    -------
    Any
        The concrete fixture value referenced by ``request.param``.
    """
    return request.getfixturevalue(request.param)


# ───────────────────── test buckets ─────────────────────
_EXTRACTION_CASES: Iterable[pytest.param] = [
    pytest.param("sample_pdf_path", False, id="pdf-path"),
    pytest.param("sample_pdf_bytes", False, id="pdf-bytes"),
    pytest.param("sample_docx_path", False, id="docx-path"),
    pytest.param("sample_docx_bytes", False, id="docx-bytes"),
    pytest.param("pptx_path", True, id="pptx-path"),
    pytest.param("pptx_bytes", True, id="pptx-bytes"),
]


@pytest.mark.integration
@pytest.mark.parametrize(("src", "needs_pptx"), _EXTRACTION_CASES, indirect=("src",))
def test_extract_smoke(
    src: Any,
    ux,
    unstructured_available: bool,
    pptx_available: bool,
    needs_pptx: bool,
) -> None:
    """
    Smoke-test extraction for every supported input.

    The test asserts three conditions:

    1. At least one element is returned.
    2. Every element passes :pyfunc:`_assert_valid_element`.
    3. A *second* extraction with identical input returns an *identical* list,
       demonstrating determinism.

    Parameters
    ----------
    src
        Sample document supplied by the parametrised ``src`` fixture.
    ux
        Fixture-provided *UnstructuredExtractor* instance.
    unstructured_available, pptx_available, needs_pptx
        Auxiliary boolean flags that decide whether the test should run.
    """
    if needs_pptx and not pptx_available:
        pytest.skip("python-pptx not installed")

    elements = list(ux.extract(src))
    assert elements, "extractor returned zero elements"

    for el in elements:
        _assert_valid_element(el)

    assert elements == list(ux.extract(src)), "extractor not idempotent"


# ───────────────── ancillary logic ─────────────────
@pytest.mark.parametrize(
    "coords, expected",
    [
        (None, None),
        (
            SimpleNamespace(
                points=[
                    SimpleNamespace(x=1, y=2),
                    SimpleNamespace(x=3, y=4),
                ]
            ),
            [(1, 2), (3, 4)],
        ),
        (type("C", (), {"to_dict": lambda self: {"x": 1}})(), {"x": 1}),
        (type("W", (), {"__str__": lambda self: "weird"})(), "weird"),
    ],
    ids=["None", "points", "to_dict", "fallback"],
)
def test_coords_to_jsonable_all_paths(ux, coords: Any, expected: Any) -> None:
    """
    Validate *all* code-paths of ``_coords_to_jsonable``.

    Acceptable conversions
    ----------------------
    * ``None`` → ``None``
    * Object with ``points`` attribute → list of ``(x, y)`` tuples
    * Object exposing ``to_dict`` → the returned dictionary
    * Fallback → ``str(obj)``

    Parameters
    ----------
    ux
        Fixture-provided *UnstructuredExtractor* instance.
    coords
        Synthetic coordinate object crafted for the specific test case.
    expected
        Expected JSON-serialisable result.
    """
    assert ux._coords_to_jsonable(coords) == expected  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "suffix, supported",
    [(".pdf", True), (".docx", True), (".pptx", True), (".foo", False)],
)
def test_supports_suffix_probe(
    tmp_path: Path, ux, suffix: str, supported: bool
) -> None:
    """
    Probe :pymeth:`supports` across known and unknown suffixes.

    The extractor should return ``True`` for recognised formats and ``False``
    otherwise.  The check is performed for both *Path* and *str* inputs.

    Parameters
    ----------
    tmp_path
        Built-in pytest fixture providing a temporary directory.
    ux
        Fixture-provided *UnstructuredExtractor* instance.
    suffix, supported
        Parameterised pairs indicating the file suffix to probe and the
        expected boolean result.
    """
    path = tmp_path / f"sample{suffix}"
    path.write_bytes(_HEADERS.get(suffix, b"dummy"))

    assert ux.supports(path) is supported
    assert ux.supports(str(path)) is supported


def test_extract_rejects_unknown_suffix(tmp_path: Path, ux) -> None:
    """
    The extractor must *gracefully* skip unsupported formats.

    Behaviour
    ---------
    * ``supports`` returns ``False``.
    * ``extract`` yields an **empty** iterator (converted to an empty list).
    """
    dummy = tmp_path / "sample.foo"
    dummy.write_text("irrelevant", encoding="utf-8")

    assert not ux.supports(dummy)
    assert list(ux.extract(dummy)) == []
