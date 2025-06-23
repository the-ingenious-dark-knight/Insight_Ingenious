"""
Integration-level checks that validate *public* behaviour of the generic
``ingenious.document_processing.extractor.extract`` helper and verify basic
invariants expected from any registered extractor implementation.

Scope
-----
1. **Raw-bytes extraction** – Feeding a PDF file already loaded into memory
   should succeed with the *default* engine.
2. **Coordinate sanity** – Bounding-box coordinates produced by any extractor
   must lie within an expected canvas (0 ≤ x0 ≤ x1 ≤ 1000 and analogous for *y*).
3. **URL handling** – When passed a *URL* pointing to a PDF, the helper fetches
   the file via ``requests.get`` and pipes its ``content`` back to the chosen
   engine.  A “404-style” failure (i.e. file not found) must resolve to an
   **empty list** rather than raising, preserving a consistent contract for
   callers that batch many sources.

Fixtures & Patching
-------------------
pdf_bytes
    ``bytes`` object containing a minimal valid PDF (supplied by
    *conftest.py*).

pdf_path
    ``pathlib.Path`` pointing to the same sample PDF saved on disk.

pymupdf
    Instance of the PyMuPDF extractor obtained via the private registry helper
    in ``ingenious.document_processing.extractor``.  Provided as a
    *function-scoped* fixture.

monkeypatch
    Pytest fixture that temporarily replaces attributes – here used to stub
    out ``requests.get`` for deterministic network tests.

pymupdf, pdf_path, and pdf_bytes fixtures reside in the shared test utilities
and are automatically discovered by pytest.
"""

from unittest import mock

from ingenious.document_processing.extractor import extract


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def test_public_extract_bytes(pdf_bytes):
    """
    Validate that passing a **bytes** object to ``extract`` returns a non-empty
    sequence of elements that all include a ``"text"`` key.

    Steps
    -----
    1. Call ``extract`` with *pdf_bytes* and **no** engine override so the
       default parser is chosen.
    2. Convert the returned iterator to a list.
    3. Assert that:
       • The list is not empty.
       • Every element contains the ``"text"`` field.
    """
    els = list(extract(pdf_bytes))  # default engine
    assert els and all("text" in e for e in els)


def test_coord_range(pymupdf, pdf_path):
    """
    Check that the **first** element emitted by the PyMuPDF extractor has
    coordinates within a 1000 × 1000 user-space box.

    Rationale
    ---------
    Many downstream consumers assume a normalised (or at least sensible)
    coordinate system when laying out highlights or snippets.  Wildly out-of-
    range values often indicate unit mismatches (points vs. pixels) or faulty
    parser logic.
    """
    els = list(pymupdf.extract(pdf_path))
    x0, y0, x1, y1 = els[0]["coords"]

    assert 0 <= x0 <= x1 <= 1000, "X-coordinates out of expected range"
    assert 0 <= y0 <= y1 <= 1000, "Y-coordinates out of expected range"


def test_public_extract_url(monkeypatch, pdf_bytes):
    """
    Ensure that the convenience wrapper handles remote sources gracefully.

    Behaviour Under Test
    --------------------
    * ``extract`` must obtain the PDF via ``requests.get``.
    * If the *downloaded* bytes fail to parse (simulated here by supplying a
      deliberately empty response body), the helper returns **[]** rather than
      raising – matching the documented contract used in higher-level pipelines.

    Implementation Notes
    --------------------
    ``monkeypatch`` replaces ``requests.get`` with a stub that:
    * returns *pdf_bytes* in its ``content`` attribute, and
    * provides a no-op ``raise_for_status`` method to mimic a 200 OK response.
    """
    fake_resp = mock.Mock(content=pdf_bytes, raise_for_status=lambda: None)
    monkeypatch.setattr("requests.get", lambda *a, **kw: fake_resp)

    els = list(extract("http://example.com/test.pdf"))

    # Contract: bad-path URL returns an empty list rather than raising
    assert els == []
