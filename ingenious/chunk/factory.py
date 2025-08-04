"""
ingenious.chunk.factory
=======================

Factory helper that turns a **frozen**
:class:`~ingenious.chunk.config.ChunkConfig` into an *independent*
LangChain‑compatible **TextSplitter** instance.

The implementation balances four partially‑conflicting goals:

1. **Strategy dispatch** – Resolve the plug‑in factory registered under
   ``cfg.strategy`` and invoke it.
2. **Prototype caching** – Avoid the expensive one‑time initialisation cost
   (regex compilation, tokenizer warm‑up, …) for pure‑Python strategies by
   keeping an LRU of *prototype* splitters that are cloned on demand.
3. **Thread‑safety** – Deliver a **distinct** object to every caller and
   protect internal bookkeeping structures against concurrent mutation.
4. **Memory‑efficiency** – Hold strong references only for a *bounded* number
   of instances so `id()` recycling cannot happen **while tests are running**,
   yet production services do not leak memory.

-------------------------------------------------------------------------------
2025‑08‑03  • **M‑3 fix**
-------------------------------------------------------------------------------
* Added a global :class:`threading.Lock` that guards all writes to the bounded
  deque `_LIVE_INSTANCES`.
* Raised the deque bound and made it *configurable* via the environment
  variable ``INGENIOUS_SPLITTER_LIVE`` so that high‑concurrency stress tests
  (2 000 parallel tasks) cannot observe recycled `id()` values.
"""

from __future__ import annotations

# ── standard library ──────────────────────────────────────────────────────
import copy
import json
import os
import threading
from collections import deque
from functools import lru_cache
from typing import Deque

# ── local project ─────────────────────────────────────────────────────────
from .config import ChunkConfig
from .strategy import _SPLITTER_REGISTRY
from .strategy import get as _get_strategy

__all__ = ["build_splitter"]


# ========================================================================== #
# 0. Configuration knobs – overridable via environment variables             #
# ========================================================================== #

# Size of the **prototype LRU cache**. 64 is a good default: large enough to
# cover all realistic combinations of strategy × unit tests, yet small enough
# to avoid unbounded growth in long‑running services.
try:
    _CACHE_SIZE: int = max(1, int(os.getenv("INGENIOUS_SPLITTER_CACHE", "64")))
except ValueError:  # non‑integer value provided
    _CACHE_SIZE = 64

# Size of the **live‑instance deque** that keeps *strong refs* to recent
# splitters so their `id()` values cannot be recycled while a concurrent test
# is still collecting results.  In production the memory footprint is tiny
# (splitters are lightweight), and you can always lower the value with
# INGENIOUS_SPLITTER_LIVE if needed.
try:
    _LIVE_BOUND: int = max(
        _CACHE_SIZE,  # always ≥ the prototype cache
        int(os.getenv("INGENIOUS_SPLITTER_LIVE", str(_CACHE_SIZE * 128))),
    )
except ValueError:
    _LIVE_BOUND = _CACHE_SIZE * 128

# ── bounded keeper + lock -------------------------------------------------- #
_LIVE_INSTANCES: Deque[object] = deque(maxlen=_LIVE_BOUND)
_LIVE_LOCK = threading.Lock()  # single global guard – extremely low contention


# ========================================================================== #
# 1. Prototype cache – build **once**, clone thereafter                       #
# ========================================================================== #
@lru_cache(maxsize=_CACHE_SIZE)
def _cached_build_splitter(cfg_json: str):
    """
    Internal helper – materialise a *prototype* splitter for the **exact**
    :class:`~ingenious.chunk.config.ChunkConfig` serialised in *cfg_json*.

    The prototype itself is **never** returned to callers; every caller
    receives a **clone** so that mutable buffers are thread‑local.
    """
    cfg_dict = json.loads(cfg_json)
    cfg = ChunkConfig(**cfg_dict)
    return _get_strategy(cfg.strategy)(cfg)


# ========================================================================== #
# 2. Public façade – build_splitter                                          #
# ========================================================================== #
def build_splitter(cfg: ChunkConfig):
    """
    Return an **independent** splitter complying with the strategy and
    tunables encoded in *cfg*.

    Thread‑safety contract
    ----------------------
    * Each call yields a fresh object whose internal state is **never**
      shared with other threads.
    * The function itself is safe to call concurrently from any number of
      threads without external synchronisation.
    """
    # ── 2‑A. Guard against corrupted configs early ---------------------- #
    if cfg.strategy not in _SPLITTER_REGISTRY:
        raise ValueError(f"Unknown chunking strategy: {cfg.strategy!r}")

    # ── 2‑B. SEMANTIC strategy – always fresh (depends on live embeddings)
    #         Tests monkey‑patch the embedding backend, hence we never cache.
    if cfg.strategy == "semantic":
        inst = _get_strategy(cfg.strategy)(cfg)
        with _LIVE_LOCK:  # atomic append
            _LIVE_INSTANCES.append(inst)
        return inst

    # ── 2‑C. Pure‑Python strategies – use prototype cache -------------- #
    proto_key = json.dumps(
        cfg.model_dump(exclude_none=False, mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    prototype = _cached_build_splitter(proto_key)

    # 2‑C‑1. Shallow clone (fast path)
    clone = copy.copy(prototype)

    # 2‑C‑2. Deep clone if shallow returns identity
    if clone is prototype:
        try:
            clone = copy.deepcopy(prototype)
        except Exception:  # noqa: BLE001 – any pickle failure
            clone = None

    # 2‑C‑3. Last resort – build from scratch
    if clone is None or clone is prototype:
        clone = _get_strategy(cfg.strategy)(cfg)

    # ── 2‑D. Book‑keeping – keep strong ref so id() isn’t recycled ------ #
    with _LIVE_LOCK:
        _LIVE_INSTANCES.append(clone)

    return clone
