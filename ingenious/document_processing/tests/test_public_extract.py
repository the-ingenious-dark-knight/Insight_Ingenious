"""
Public-API equivalence-layer test for :pyfunc:`ingenious.document_processing.extract`.

Purpose
-------
The helper function :pyfunc:`ingenious.document_processing.extract` accepts an
optional ``engine`` keyword to select a specific extractor implementation.
If the caller omits this argument the helper falls back to the **default
engine** configured in the *extractor* sub-package (currently “pymupdf”).

This test verifies that:

* Calling the helper **with** ``engine="pymupdf"`` yields **exactly the same**
  list of element dictionaries as calling it **without** the parameter, thereby
  confirming that the public wrapper is a *thin façade* and does not mutate or
  post-process results.

Fixtures
--------
pdf_path
    A :class:`pathlib.Path` fixture provided by *conftest.py* that points to a
    small, deterministic sample PDF used across the extractor test-suite.
"""

from ingenious.document_processing import extract


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def test_public_extract_is_thin_wrapper(pdf_path):
    """
    Assert that explicit and implicit engine selection are functionally
    identical.

    Steps
    -----
    1. Call :pyfunc:`extract` with *pdf_path* and ``engine="pymupdf"``.
    2. Call :pyfunc:`extract` again with *pdf_path* **but without** the
       ``engine`` argument (thereby using the package-level default).
    3. Compare the two result lists for deep equality.

    A mismatch would indicate that the wrapper performs additional processing
    or that the default engine has diverged from “pymupdf”, both of which
    should trigger a code review.
    """
    els_engine = list(extract(pdf_path, engine="pymupdf"))
    els_default = list(extract(pdf_path))  # default is pymupdf

    assert els_engine == els_default
