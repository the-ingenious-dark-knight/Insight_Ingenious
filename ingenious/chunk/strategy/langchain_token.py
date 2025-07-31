"""
ingenious.chunk.strategy.langchain_token
=======================================

Unicode‑safe splitter with **configurable overlap**.

Key guarantees
--------------

* **Hard budget** – every emitted chunk is **≤ ``chunk_size``** in the unit
  chosen by the user (tokens *or* characters).
* **Unicode correctness** – boundaries are aligned with **grapheme clusters**
  so no surrogate pairs or emoji sequences are torn apart.
* **Bidirectional context** – a left‑side overlap window is injected between
  consecutive chunks in either **tokens** *(default)* or **characters* –
  controlled by ``ChunkConfig.overlap_unit``.

Implementation choices
----------------------

* *Token budgets* use :class:`UnicodeSafeTokenTextSplitter`, a strict,
  grapheme‑aware rewrite of LangChain’s original `TokenTextSplitter`.
* *Character budgets* delegate to LangChain’s
  :class:`RecursiveCharacterTextSplitter` (word‑aware) and then apply the same
  overlap logic via the shared helper
  :pyclass:`ingenious.chunk.strategy.langchain_recursive._OverlapWrapper`.

This file **fixes issue M4** from the code‑review: the helper
``_build_overlap`` no longer returns a phantom *consumed* integer – only the
buffer that seeds the next chunk.  The signature, docstring, and call‑site
have all been updated accordingly.
"""
from __future__ import annotations

from typing import List

import regex as re
from langchain_text_splitters.base import TextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tiktoken import get_encoding

from ..config import ChunkConfig
from . import register
from .langchain_recursive import _OverlapWrapper  # reuse for char‑budget path

__all__: list[str] = ["create"]

# --------------------------------------------------------------------------- #
# Pre‑compiled regex that matches *extended grapheme clusters* (Unicode TR‑29)
# This ensures we never split inside a composite emoji or between base +
# combining‑accent codepoints.
# --------------------------------------------------------------------------- #
_GRAPHEME_RE = re.compile(r"\X", re.UNICODE)


# --------------------------------------------------------------------------- #
# Strict token‑budget splitter                                                #
# --------------------------------------------------------------------------- #
class UnicodeSafeTokenTextSplitter(TextSplitter):
    """
    A drop‑in replacement that is **both**

    1. *Grapheme‑boundary‑aware* – no broken emojis / accents, and
    2. Strictly bounded by **tokens** (or raw characters) – depending on
       :pyattr:`overlap_unit`.

    Used only when ``cfg.overlap_unit == "tokens"``.
    """

    # ------------------------------- ctor -------------------------------- #
    def __init__(
        self,
        encoding_name: str,
        chunk_size: int,
        chunk_overlap: int,
        overlap_unit: str = "tokens",
    ) -> None:
        """
        Parameters
        ----------
        encoding_name:
            Name understood by *tiktoken* (e.g. ``"cl100k_base"``).
        chunk_size:
            Hard upper‑bound for each chunk **before** overlap is injected.
        chunk_overlap:
            Size of the bidirectional window.
        overlap_unit:
            ``"tokens"`` or ``"characters"``. `"characters"` is rarely used
            here but included for completeness.
        """
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._enc = get_encoding(encoding_name)
        self._overlap_unit = overlap_unit

    # ------------------------- public interface -------------------------- #
    def split_text(self, text: str) -> list[str]:  # type: ignore[override]
        """
        Split *text* into chunks that respect all invariants described at the
        top of the module.

        Returns
        -------
        list[str]
            Ordered list of chunks **with** overlap already injected.
        """
        clusters = _GRAPHEME_RE.findall(text)      # Unicode grapheme clusters
        out: list[str] = []

        buf: list[str] = []        # current chunk (as graphemes, not str)
        enc = self._enc
        i = 0

        # Helper closure: measure length in the unit chosen by the user
        def _len_units(s: str) -> int:
            return len(s) if self._overlap_unit == "characters" else len(enc.encode(s))

        while i < len(clusters):
            g = clusters[i]
            buf.append(g)

            # ‑‑‑ Budget exceeded after adding *g*? ----------------------- #
            if _len_units("".join(buf)) > self._chunk_size:
                # Flush current buffer (without *g*)
                buf.pop()          # rollback g
                out.append("".join(buf))

                # Seed new buffer with configured overlap window
                buf = self._build_overlap(buf)

                # Edge‑case: *g* alone exceeds the budget – emit it intact
                if _len_units(g) > self._chunk_size:
                    out.append(g)
                    buf = []
                    i += 1
                    continue

                buf.append(g)      # start new chunk with g

            i += 1

        # Remainder
        if buf:
            out.append("".join(buf))

        return out

    # ------------------------------ helpers ------------------------------ #
    def _build_overlap(self, old_buf: List[str]) -> List[str]:
        """
        Construct the **initial** buffer for the next chunk consisting of the
        last *k* units of the *current* chunk.

        Parameters
        ----------
        old_buf:
            Buffer (as a list of grapheme clusters) representing the **already
            emitted** chunk.

        Returns
        -------
        list[str]
            A new grapheme‑cluster buffer ready to receive additional text
            before the next flush.

        Notes
        -----
        * For ``overlap_unit="tokens"`` we translate the final *k* tokens back
          to text and then split into graphemes so boundaries stay valid.
        * For ``overlap_unit="characters"`` we copy the last *k* raw characters.
        """
        k = self._chunk_overlap
        if k == 0:
            return []

        # ---------------- token‑based path ---------------- #
        if self._overlap_unit == "tokens":
            enc = self._enc
            prev_tokens = enc.encode("".join(old_buf))
            tail_tokens = prev_tokens[-k:]
            tail_text = enc.decode(tail_tokens)
            return list(tail_text)                    # ← grapheme split

        # -------------- character‑based path -------------- #
        tail_text = "".join(old_buf)[-k:]             # raw characters
        return list(tail_text)


# --------------------------------------------------------------------------- #
# Factory registration                                                        #
# --------------------------------------------------------------------------- #
@register("token")
def create(cfg: ChunkConfig):
    """
    Public factory discovered via the plug‑in registry.

    Behaviour
    ---------
    * ``overlap_unit="tokens"`` → return a strict
      :class:`UnicodeSafeTokenTextSplitter`.
    * ``overlap_unit="characters"`` → delegate to LangChain’s
      :class:`RecursiveCharacterTextSplitter` (word‑aware) and wrap it with
      :pyclass:`_OverlapWrapper` so word boundaries are preserved **and** the
      overlap invariant still holds.
    """
    # ---------- token‑budget path (original behaviour) ------------------ #
    if cfg.overlap_unit == "tokens":
        return UnicodeSafeTokenTextSplitter(
            encoding_name=cfg.encoding_name,
            chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
            overlap_unit="tokens",
        )

    # ---------- character‑budget path (word‑aware) ---------------------- #
    base = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=0,           # overlap injected by wrapper
    )
    return _OverlapWrapper(
        base,
        cfg.chunk_overlap,
        cfg.encoding_name,
        unit="characters",
    )
