"""Insight Ingenious – edge‑case tests for :pyfunc:`_iter_sources`
================================================================
This module exercises *corner‑case* scenarios for the private helper
:pyfunc:`ingenious.document_processing.cli._iter_sources` – the low‑level
iterator responsible for translating a user‑supplied CLI argument into a
sequence of ``(label, src)`` pairs, where *src* is either a
:pyclass:`pathlib.Path` (for local files) or a ``bytes`` object (for
remote downloads).

The *happy‑path* behaviours are already covered in
``test_cli.py``.  Here we focus exclusively on **edge conditions** that
could otherwise slip through manual testing:

* **HTTP 404** – ensuring that network failures surface as
  :class:`requests.HTTPError` exceptions and are *not* swallowed by the
  helper.
* **Empty directory** – confirming that supplying an existing but empty
  directory yields an *empty iterator* rather than raising or yielding
  unexpected paths.

Maintaining explicit tests for these cases guards against future
regressions in path‑resolution or error‑handling logic.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from requests import HTTPError

from ingenious.document_processing.cli import _iter_sources

# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #


def test_iter_sources_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP 404 responses **must propagate** as :class:`HTTPError`.

    We monkey‑patch :pyfunc:`requests.get` inside the CLI module so that it
    raises an :class:`HTTPError` immediately.  The expectation is that
    calling :pyfunc:`_iter_sources` with the offending URL bubbles the
    exception upward; the helper should *not* attempt to catch or convert
    it.
    """

    def _raise(*_args, **_kwargs):  # noqa: D401  (simple stub)
        """Inline stub that *always* raises *HTTPError*."""

        raise HTTPError("404 – Not Found")

    monkeypatch.setattr(
        "ingenious.document_processing.cli.requests.get", _raise, raising=True
    )

    with pytest.raises(HTTPError):
        next(_iter_sources("http://example.com/missing.pdf"))


def test_iter_sources_empty_dir(tmp_path: Path) -> None:
    """An empty directory should yield **no results**.

    The helper recurses using :pyfunc:`pathlib.Path.rglob`; when pointed at
    an empty directory it should simply return an *exhausted iterator*
    rather than raising an error or yielding spurious entries.
    """

    assert list(_iter_sources(tmp_path)) == [], (
        "Iterator should be empty for an empty dir"
    )
