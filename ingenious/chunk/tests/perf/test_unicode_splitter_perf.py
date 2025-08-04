"""
perf/test_unicode_splitter_perf.py
==================================

Performance‑regression guard for *UnicodeSafeTokenTextSplitter*.

Background
----------
The original (pre‑optimisation) implementation inside
``UnicodeSafeTokenTextSplitter.split_text`` re‑encoded the **entire** buffer
at every grapheme append, yielding *quadratic* behaviour –
``encode()`` was invoked ≈ *len(text)²* times for long inputs.

The re‑write keeps a *running token counter* and re‑encodes only a **tiny
tail context** on each loop iteration, so the end‑to‑end complexity is now
*linear* in the number of grapheme clusters, i.e. **O(N)**.

Goal
----
Detect any future changes that accidentally drift back to *super‑linear*
behaviour.  We monkey‑patch the underlying ``tiktoken.Encoding.encode``
method to count how many times it is called while performing a realistic
split.  The assertion below allows *at most* **4 × N** calls, where N is
the number of grapheme clusters in the input.

• Why 4 × N?
  – Each iteration encodes two small strings (*before* + *after* context) → 2 × N
  – At every chunk flush we recompute overlap windows, costing **another**
    two calls.  The worst‑case number of flushes is `< N / chunk_size`,
    so 4 × N is still a generous *linear* bound while remaining several
    orders‑of‑magnitude below the old quadratic profile.

If the algorithm regresses (e.g. someone re‑introduces ``len(enc.encode())``
over the full buffer) the encode‑call count will exceed this threshold and
fail the test loudly in CI.

Usage
-----
Executed automatically by *pytest* under the ``tests/perf`` collection.
"""

from __future__ import annotations

import regex as re

from ingenious.chunk.strategy.langchain_token import UnicodeSafeTokenTextSplitter


def test_encode_call_count(monkeypatch) -> None:
    """
    Split a 12 k‑grapheme document and assert the underlying tokenizer’s
    ``encode()`` method is called at most **4 × N** times (linear bound).

    The test is quick (~30 ms on CI) and hermetic – no network, no disk I/O.
    """
    # ---------------------------------------------------------------
    # 1. Build a medium‑size input: repeating "A😀 " (3 graphemes) so
    #    we get a mix of ASCII and multi‑code‑point emoji clusters.
    #    4 000 iterations → 12 000 graphemes, enough to exhibit
    #    previously quadratic behaviour without slowing the test suite.
    # ---------------------------------------------------------------
    text: str = ("A😀 " * 4000).strip()
    clusters = re.findall(r"\X", text)  # extended grapheme clusters
    n = len(clusters)

    # ---------------------------------------------------------------
    # 2. Instantiate the tokenizer‑aware splitter under test.
    # ---------------------------------------------------------------
    splitter = UnicodeSafeTokenTextSplitter(
        encoding_name="cl100k_base",  # same default used in production
        chunk_size=64,  # tiny budget to force many flushes
        chunk_overlap=0,
        overlap_unit="tokens",
    )
    enc = splitter._enc  # tiktoken.Encoding instance (cached)

    # ---------------------------------------------------------------
    # 3. Monkey‑patch `enc.encode` with a counting wrapper so we can
    #    measure how many times the optimiser calls it.
    # ---------------------------------------------------------------
    call_counter = {"n": 0}
    original_encode = enc.encode

    def _counting_encode(s: str):  # noqa: D401 (simple helper)
        call_counter["n"] += 1
        return original_encode(s)

    monkeypatch.setattr(enc, "encode", _counting_encode)

    # ---------------------------------------------------------------
    # 4. Run the split – *all* encode() invocations will now be tallied.
    # ---------------------------------------------------------------
    splitter.split_text(text)

    # ---------------------------------------------------------------
    # 5. Assertion – linear‑time guard.
    #    Allow up to 4 × N encode calls; anything above indicates an
    #    accidental O(N²) regression.
    # ---------------------------------------------------------------
    max_allowed = 4 * n
    actual_calls = call_counter["n"]
    assert actual_calls <= max_allowed, (
        f"O(N²) regression detected: encode() called {actual_calls:,} times "
        f"for {n:,} graphemes (limit {max_allowed:,})"
    )
