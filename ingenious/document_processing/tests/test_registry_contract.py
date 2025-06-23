"""
Registry and Loader Contract Tests for Document Processing Extractors
====================================================================

This **pytest** module serves as an executable specification for the public
contract exposed by the *extractor registry* located in
:pyfile:`ingenious.document_processing.extractor`.  The registry provides two
critical entry points used throughout the Insight Ingenious codebase:

* :pydata:`_ENGINES` — an immutable mapping of symbolic engine names to their
  corresponding extractor implementations; this list defines the *supported
  surface area* for the document‑processing subsystem.
* :pyfunc:`_load` — a lightweight factory that returns a ready‑to‑use extractor
  instance for a given engine name.  Internally, the factory applies an
  **LRU‑cache** so repeated invocations with the same engine name return the
  *same* in‑memory object.  This design guarantees that expensive resources
  (GPU memory, lazy model initialisation, etc.) are shared rather than
  duplicated.

The tests below codify two **non‑negotiable invariants** that every extractor
implementation must uphold:

1. **Singleton behaviour** — A call sequence
   ``x = _load(name); y = _load(name)`` must satisfy ``x is y``.  Violations
   indicate either broken cache semantics or side effects that undermine
   thread safety and memory usage guarantees.
2. **Remote resource support** — All registered extractors must be prepared to
   handle HTTP or HTTPS documents.  The contract is expressed via the boolean
   :pyfunc:`supports` predicate.  Even engines that ultimately stream the
   content locally should *advertise* that they accept network addresses; the
   orchestration layer will provide the actual bytes.

Fixtures
--------
``pdf_path``
    A *path‑like* fixture supplied by the project‑level ``conftest.py``.  It
    points to a sample PDF shipped with the test suite.  We only reuse the
    filename to build a deterministic remote URL; no network calls are made
    during the test run.

Running the tests
-----------------
Execute the full contract suite via **pytest**:

>>> uv run pytest ingenious/document_processing/tests/test_registry_contract.py

All assertions carry descriptive messages so that CI logs remain actionable
without having to reproduce the failure locally.
"""

from __future__ import annotations

import pytest

from ingenious.document_processing.extractor import _ENGINES, _load

__all__ = [
    "test_load_returns_singleton",
    "test_supports_accepts_remote_url",
]


@pytest.mark.parametrize("engine_name", sorted(_ENGINES))
def test_load_returns_singleton(engine_name: str) -> None:
    """Validate the *singleton* semantics of :pyfunc:`_load`.

    Repeated invocations with an identical ``engine_name`` must yield the
    *exact* same object instance.  The guarantee is essential to prevent
    runaway memory consumption and to ensure that expensive initialisation
    occurs only once per process.

    Parameters
    ----------
    engine_name:
        Symbolic key referencing an extractor implementation within
        :pydata:`_ENGINES`.
    """
    first_instance = _load(engine_name)
    second_instance = _load(engine_name)

    assert first_instance is second_instance, (
        "_load should return the same cached instance on repeated calls"
    )


def test_supports_accepts_remote_url(pdf_path) -> None:
    """Assert that every extractor **claims** support for remote URLs.

    The registry does not dictate *how* an extractor consumes a remote
    resource—it may stream, cache, or download eagerly—but it *must* indicate
    capability via :pyfunc:`supports`.  The test fabricates a synthetic HTTP
    URL based solely on the sample PDF's filename to avoid external network
    dependencies while still inspecting the relevant code path.

    Parameters
    ----------
    pdf_path: pathlib.Path
        Fixture supplying the path to a sample PDF packaged with the test
        suite.  Only the ``name`` attribute is used.
    """
    remote_url = f"http://example.com/{pdf_path.name}"

    for engine_name in _ENGINES:
        engine = _load(engine_name)
        assert engine.supports(remote_url) is True, (
            f"{engine_name} should report support for remote URLs"
        )
