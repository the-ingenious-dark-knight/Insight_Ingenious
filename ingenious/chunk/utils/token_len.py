# ingenious/chunk/utils/token_len.py
"""Fast, cached token‑length helper used by multiple strategies.

* **LRU bound** – the underlying ``tiktoken.Encoding`` objects are now cached
  with a **bounded** LRU so long‑running workers cannot leak memory when they
  encounter many distinct model names.
* The size is configurable via the environment variable
  ``INGENIOUS_TOKEN_CACHE_SIZE``; default is 32, mirroring the splitter cache
  design.
"""

from __future__ import annotations

import os

from functools import lru_cache

from tiktoken import get_encoding


# --------------------------------------------------------------------------- #
# Configurable cache bound                                                    #
# --------------------------------------------------------------------------- #
_CACHE_SIZE: int
try:
    _CACHE_SIZE = max(1, int(os.getenv("INGENIOUS_TOKEN_CACHE_SIZE", "32")))
except ValueError:  # non‑integer → fall back to default
    _CACHE_SIZE = 32

@lru_cache(maxsize=_CACHE_SIZE)
def _enc(name: str):
    """Return (and memoise) a tiktoken encoding instance."""
    return get_encoding(name)


def token_len(text: str, enc_name: str = "cl100k_base") -> int:
    """Number of tokens in *text* for the requested encoding."""
    return len(_enc(enc_name).encode(text))
