"""
Top‑level convenience exports for the Ingenious chunking feature.
Keeps public symbols stable regardless of internal refactors.
"""

from .config import ChunkConfig
from .factory import build_splitter

__all__ = ["ChunkConfig", "build_splitter"]
