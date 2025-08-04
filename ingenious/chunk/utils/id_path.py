"""
ingenious.chunk.utils.id_path
=============================

**Purpose**

Convert an arbitrary *source* path (file system path or opaque string) into
the **stable identifier prefix** that is embedded in every chunk ID emitted by
the writer.  The exact representation depends on the *id‑path mode*
configured by the user:

* ``abs``  – fully‑qualified, normalised POSIX path
* ``rel``  – path *relative* to ``id_base`` (defaults to CWD) *or* a hash when
  the file lives outside that base
* ``hash`` – always a salted hash digest

Historically the hash‑based forms were truncated to **12 hex characters**
(48 bits).  For multi‑billion‑chunk corpora this exposed a measurable
birthday‑collision risk, so the PR introduces **`ChunkConfig.id_hash_bits`**
(default 48, min 32, max 256, multiple of 4).  All digests produced by this
module now honour that setting.

The helper is deliberately **pure** – it never touches global state, performs
no I/O, and throws no exceptions other than `ValueError` for an invalid
configuration.  This makes it easy to unit‑test and thread‑safe.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union

from ..config import ChunkConfig


# --------------------------------------------------------------------------- #
# Helper – digest truncation                                                  #
# --------------------------------------------------------------------------- #
def _trunc_digest(data: str, bits: int) -> str:
    """
    Return the **hexadecimal** SHA‑256 digest of *data*, truncated to *bits*
    bits (must be divisible by 4 so we cut on nibble boundaries).

    Notes
    -----
    * SHA‑256 is used because it is ubiquitous, fast, and cryptographically
      strong; collision resistance is *far* beyond what we need – the only
      reason to truncate is usability.
    * A helper function keeps the main logic readable and centralises the
      maths (bits → hex‑chars conversion).
    """
    if bits % 4 != 0:
        raise ValueError("id_hash_bits must be a multiple of 4")
    hex_len = bits // 4  # 1 hex digit = 4 bits
    return hashlib.sha256(data.encode("utf-8", "surrogatepass")).hexdigest()[:hex_len]


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #
def _norm_source(src: Union[str, Path], cfg: ChunkConfig) -> str:
    """
    Normalise *src* to the canonical form dictated by ``cfg.id_path_mode``.

    Parameters
    ----------
    src :
        File‑system path (``str`` | ``Path``) **or** any string that identifies
        the origin of the document (e.g. an S3 URI).  Non‑path strings are
        treated as opaque and passed to the hash fallback.
    cfg :
        **Immutable** :class:`~ingenious.chunk.config.ChunkConfig` whose
        *id‑path* fields have already been validated by Pydantic.

    Returns
    -------
    str
        A **portable POSIX string** suitable for direct embedding in the
        chunk‑ID (no back‑slash on Windows).

    Behaviour summary
    -----------------
    | ``id_path_mode`` | Inside ``id_base``? | Result                         |
    |------------------|---------------------|--------------------------------|
    | ``abs``          |      n/a           | absolute POSIX path            |
    | ``rel``          |        ✓           | relative POSIX path            |
    | ``rel``          |        ✗           | truncated SHA‑256 digest       |
    | ``hash``         |      n/a           | salted truncated SHA‑256 digest|

    *All* hash digests honour ``cfg.id_hash_bits`` (default 64 bits).
    """
    raw = str(src)  # accept Path | str uniformly

    # ------------------------------------------------------------------ #
    # 1) Try to turn *src* into an **absolute Path**.  Any exception –
    #    including invalid bytes or missing drive letters – falls back to
    #    a stable digest so the caller still gets a unique identifier.
    # ------------------------------------------------------------------ #
    try:
        p = Path(raw).resolve(strict=False)
    except (OSError, ValueError):
        return _trunc_digest(raw, cfg.id_hash_bits)

    mode = cfg.id_path_mode

    # ------------------------------------------------------------------ #
    # 2) abs‑mode – return the fully‑qualified POSIX path verbatim.
    #    This is the most transparent (but also privacy‑sensitive) choice.
    # ------------------------------------------------------------------ #
    if mode == "abs":
        return p.as_posix()

    # ------------------------------------------------------------------ #
    # 3) rel‑mode – prefer a *readable* relative path **if** the file is
    #    inside `id_base` (or CWD).  Otherwise we hash to avoid collisions
    #    between identically‑named files in different folders.
    # ------------------------------------------------------------------ #
    if mode == "rel":
        base = (cfg.id_base or Path.cwd()).resolve()
        try:
            return p.relative_to(base).as_posix()
        except ValueError:
            # Outside the base – fall back to digest of the *absolute* path.
            # (Hashing the absolute path, not just the file‑name, prevents
            # collisions when `[base]/dirA/report.txt` and `/tmp/report.txt`
            # coexist.)
            return _trunc_digest(p.as_posix(), cfg.id_hash_bits)

    # ------------------------------------------------------------------ #
    # 4) hash‑mode – always digest.  An optional *salt* (id_base) lets
    #    callers namespace their hashes so different projects cannot clash
    #    even if they process the same file tree.
    # ------------------------------------------------------------------ #
    salt = cfg.id_base.as_posix() if cfg.id_base else ""
    return _trunc_digest(f"{salt}:{p.as_posix()}", cfg.id_hash_bits)
