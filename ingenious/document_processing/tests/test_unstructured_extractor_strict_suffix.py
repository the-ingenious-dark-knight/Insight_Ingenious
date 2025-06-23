"""
Integration tests – strict-suffix handling for UnstructuredExtractor
===================================================================

Overview
--------
This module contains an **integration test** that verifies
:class:`ingenious.document_processing.extractor.unstructured.UnstructuredExtractor`
correctly *rejects* files whose suffix is not one of the three rich-text
types it explicitly supports:

* ``.pdf``
* ``.docx``
* ``.pptx``

A file with any other suffix must be *ignored* by the extractor:
``supports()`` must return ``False`` and ``extract()`` must yield zero
elements.

Why this matters
----------------
Rejecting unknown suffixes up-front prevents subtle downstream failures such
as:

* attempting to parse binary data with an inappropriate back-end,
* silently emitting empty output that masks data-loss bugs, or
* raising late-stage exceptions that obscure the real root cause.

Test architecture
-----------------
The test employs the classic *Arrange → Act → Assert* structure:

1. **Arrange**
   A dummy file named ``sample.foo`` is created in a temporary directory.
2. **Act & Assert**
   * ``supports()`` is expected to return ``False``.
   * ``extract()`` is expected to return an empty iterator.

Pytest markers
--------------
* ``@pytest.mark.integration`` – isolates slower tests that rely on optional
  external dependencies.
* ``@pytest.mark.usefixtures("unstructured_available")`` – skips the test when
  the *unstructured* library is not installed, avoiding false negatives.

Expected environment
--------------------
* Python 3.9 or later (the code uses postponed evaluation of annotations).
* The *unstructured* extra must be available for the extractor to load.

Running the test
----------------
From the project root:

>>> pytest -m integration tests/integration/test_unstructured_suffix.py

The test passes if **no assertions fail** and pytest exits with status 0.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ingenious.document_processing.extractor import _load


@pytest.mark.integration
@pytest.mark.usefixtures("unstructured_available")
def test_extract_skips_unknown_suffix(tmp_path: Path) -> None:
    """
    Verify that *UnstructuredExtractor* ignores a file whose suffix is not
    supported.

    The extractor must signal non-support via ``supports()`` and must *not*
    emit any elements from ``extract()``.

    Parameters
    ----------
    tmp_path : pathlib.Path
        A pytest-supplied temporary directory.  The test creates
        ``sample.foo`` here to ensure a clean, self-contained environment.

    Assertions
    ----------
    * ``supports(dummy_file)`` returns ``False``.
    * ``extract(dummy_file)`` returns an iterator that is empty after
      materialisation.

    Notes
    -----
    The dummy file’s content is irrelevant because the extractor should never
    attempt to open it once the suffix check fails.
    """
    # ------------------------------------------------------------------ #
    # Arrange – create a dummy file with an unsupported suffix.
    # ------------------------------------------------------------------ #
    dummy_file: Path = tmp_path / "sample.foo"
    dummy_file.write_text(
        "Alpha line\nBeta line\nGamma line\n",
        encoding="utf-8",
    )

    extractor = _load("unstructured")

    # ------------------------------------------------------------------ #
    # Act & Assert – supports() and extract() behaviour.
    # ------------------------------------------------------------------ #
    assert not extractor.supports(dummy_file), (
        "Extractor should mark .foo as unsupported"
    )

    extracted: list[dict] = list(extractor.extract(dummy_file))
    assert extracted == [], "Extractor returned elements for an unsupported suffix"
