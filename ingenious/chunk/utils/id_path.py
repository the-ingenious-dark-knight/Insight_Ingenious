from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union

from ..config import ChunkConfig


def _norm_source(src: Union[str, Path], cfg: ChunkConfig) -> str:
    """
    Convert *src* (str **or** Path) into abs / rel / hash form.

    • On any failure to resolve (null bytes, missing file, etc.) we fall back
      to a 12‑hex SHA‑256 digest — same format as ``id_path_mode="hash"``.
    """
    raw = str(src)  # unify input type

    try:
        p = Path(raw).resolve()
    except (OSError, ValueError):
        return hashlib.sha256(raw.encode("utf-8", "surrogatepass")).hexdigest()[:12]

    mode = cfg.id_path_mode

    if mode == "abs":
        return p.as_posix()

    if mode == "rel":
        base = (cfg.id_base or Path.cwd()).resolve()
        try:
            return p.relative_to(base).as_posix()
        except ValueError:
            # The file is *outside* the declared base directory.
            # Falling back to its bare file‑name risks a collision when two
            # sibling directories contain identically‑named files (e.g.,
            # “…/2024/report.txt”, “…/2025/report.txt”).
            #
            # Instead, collapse the *absolute* POSIX path into a stable,
            # 12‑hex digest – same length and character set used elsewhere.
            digest = hashlib.sha256(
                p.as_posix().encode("utf-8", "surrogatepass")
            ).hexdigest()[:12]
            return digest

    # mode == "hash"
    salt = cfg.id_base.as_posix() if cfg.id_base else ""
    return hashlib.sha256(f"{salt}:{p.as_posix()}".encode()).hexdigest()[:12]
