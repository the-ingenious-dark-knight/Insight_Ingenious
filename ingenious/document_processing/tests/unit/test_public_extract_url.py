"""
Insight Ingenious — *extract* remote-download fail-soft tests
===========================================================

This module belongs to the **unit** tier of the
``ingenious.document_processing`` test-suite.  It validates the *fail-soft*
contract of the public helper:

    >>> ingenious.document_processing.extract

*Fail-soft* means that **invalid input must never raise**; instead the function
returns an **empty list** so that downstream pipelines can continue operating.
Here we probe the most brittle branch — downloading a *remote* PDF whose byte
stream is deliberately corrupted.

Test outline
------------
1. Monkey-patch :pyfunc:`requests.get` to return a synthetic
   :class:`requests.Response` whose body contains a *minimal* but **malformed**
   PDF payload.
2. Invoke :pyfunc:`~ingenious.document_processing.extract` with a *dummy* URL
   while relying on the **default extractor** (no ``engine`` argument).
3. Assert that the return value is ``[]`` and that **no** exception escapes.
"""

from __future__ import annotations

from typing import Any

import pytest
from requests.models import Response

from ingenious.document_processing import extract

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
_CORRUPT_PDF_BYTES: bytes = (
    b"%PDF-1.7 broken\n%%EOF"  # minimal payload that crashes every PDF parser
)


# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #
def test_extract_downloads_and_fails_soft(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Ensure **fail-soft** behaviour when `extract` encounters a corrupt remote
    PDF.

    Workflow
    --------
    Arrange
        Patch :pyfunc:`requests.get` so that it returns a 200-OK
        :class:`requests.Response` whose ``content`` is a two-line, malformed
        PDF header.
    Act
        Call :pyfunc:`ingenious.document_processing.extract` with a dummy URL,
        relying on the *default* extractor (no ``engine`` argument supplied).
    Assert
        The helper **returns** an **empty list** and **raises no exception**.

    Parameters
    ----------
    monkeypatch
        Built-in *pytest* fixture allowing temporary mutation of attributes
        for the duration of the test.
    """
    # ── stub remote download ────────────────────────────────────────────
    fake_resp = Response()
    fake_resp.status_code = 200
    fake_resp._content = _CORRUPT_PDF_BYTES  # type: ignore[attr-defined]

    monkeypatch.setattr(
        "ingenious.document_processing.requests.get",
        lambda *args, **kwargs: fake_resp,
        raising=True,
    )

    # ── exercise URL branch ─────────────────────────────────────────────
    result: list[dict[str, Any]] = list(extract("http://example.com/bad.pdf"))

    # ── expectations ───────────────────────────────────────────────────
    assert result == [], "extract should fail-soft and yield an empty list"
