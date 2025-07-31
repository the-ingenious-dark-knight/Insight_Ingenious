"""
ingenious.chunk.loader
======================

Robust document‑loader that now **streams large JSON payloads** to avoid
out‑of‑memory crashes on memory‑constrained workers.

Highlights
----------
* Files ≤ ``_STREAM_THRESHOLD`` (10 MiB by default) still use the fast
  ``json.loads`` eager path – zero behaviour change for small inputs.
* Larger JSON is parsed incrementally **iff** the optional `ijson`
  dependency is present (included in the ``[chunk]`` extra).
* When a large file is encountered but `ijson` is absent, a clear,
  actionable ``RuntimeError`` is raised so users know how to proceed.
"""

from __future__ import annotations

import enum
import json
import os
from glob import glob
from pathlib import Path
from typing import Callable, Iterable, Iterator, List

import jsonlines
from langchain_core.documents import Document

try:  # optional streaming backend (pure‑Python, MIT)
    import ijson  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    ijson = None  # sentinel used later

# --------------------------------------------------------------------------- #
# Loader helpers                                                              #
# --------------------------------------------------------------------------- #
_STREAM_THRESHOLD = int(os.getenv("INGEN_JSON_STREAM_THRESHOLD", 10 << 20))  # 10 MiB


class _Mode(enum.Enum):
    SMALL = "small"      # eager json.load
    STREAM = "stream"    # incremental parse via ijson
    FAIL = "fail"        # large but no ijson – raise


def _iter_files(pattern: str) -> Iterable[Path]:
    """Yield all files under *pattern* (file, dir, or glob)."""
    p = Path(pattern)
    if p.exists():
        if p.is_file():
            yield p
        else:
            yield from (fp for fp in p.rglob("*") if fp.is_file())
    else:  # glob expansion
        yield from (Path(m) for m in glob(pattern, recursive=True) if Path(m).is_file())


_KEY_CANDIDATES = ("text", "page_content", "body")


def _extract_text(rec: dict) -> str:
    """Return the first non‑blank value among the standard keys."""
    for k in _KEY_CANDIDATES:
        v = rec.get(k, "")
        if isinstance(v, str) and v.strip():
            return v
    return ""


# --------------------------------------------------------------------------- #
# JSON helpers – streaming vs eager                                           #
# --------------------------------------------------------------------------- #
def _select_mode(path: Path) -> _Mode:
    """Choose eager vs streaming strategy based on file size & availability."""
    if path.stat().st_size <= _STREAM_THRESHOLD:
        return _Mode.SMALL
    if ijson is None:
        return _Mode.FAIL
    return _Mode.STREAM


def _stream_array(path: Path) -> Iterator[dict]:
    """Yield objects from a top‑level JSON array."""
    # 'item' token selects each array element
    with path.open("rb") as fp:
        yield from ijson.items(fp, "item")


def _stream_object(path: Path):
    """
    Incrementally yield *value* objects from a top‑level JSON **map** ::

        {
          "00001": {...},
          "00002": {...},
          ...
        }

    Each value is treated as an independent *record* and fed through the
    standard ``_extract_text`` helper.  This keeps peak RSS bounded to
    roughly the size of the **largest value**, not the entire file.
    """
    if ijson is None:  # pragma: no cover – guardian; callers check earlier
        raise RuntimeError("ijson must be installed for streaming mode")

    with path.open("rb") as fp:
        # kvitems returns an iterator of (key, value) pairs from the prefix.
        # The empty string '' selects the *root* object.
        for idx, (_, value) in enumerate(ijson.kvitems(fp, "")):
            # Support either a bare string OR an object that embeds text.
            txt = value if isinstance(value, str) else _extract_text(value)
            if isinstance(txt, str) and txt.strip():
                yield Document(
                    txt,
                    metadata={
                        "source": str(path),
                        "page": idx,      # preserve page semantics
                    },
                )


def _root_char(path: Path) -> str:
    """Return the first non‑whitespace character of the file."""
    with path.open("rb") as fp:
        while (b := fp.read(1)):
            ch = chr(b[0])
            if not ch.isspace():
                return ch
    return ""


# --------------------------------------------------------------------------- #
# Per‑extension parser functions                                              #
# --------------------------------------------------------------------------- #
def _parse_jsonl(path: Path) -> Iterator[Document]:
    with jsonlines.open(path) as rdr:
        for i, rec in enumerate(rdr):
            if (txt := _extract_text(rec)):
                yield Document(txt, metadata={"source": str(path), "page": i})


def _parse_json(path: Path) -> Iterator[Document]:
    mode = _select_mode(path)

    # ---------- eager small‑file path ------------------------------------ #
    if mode is _Mode.SMALL:
        payload = json.loads(path.read_text(encoding="utf‑8"))
        records = payload if isinstance(payload, list) else [payload]
        for i, rec in enumerate(records):
            if (txt := _extract_text(rec)):
                yield Document(txt, metadata={"source": str(path), "page": i})
        return

    # ---------- large file but cannot stream ---------------------------- #
    if mode is _Mode.FAIL:  # pragma: no cover
        size_mb = path.stat().st_size / (1 << 20)
        raise RuntimeError(
            f"{path} is {size_mb:,.1f} MB – install 'ingenious[chunk]' or "
            "'ijson' to enable streaming of large JSON files."
        )

    # ---------- streaming path (array or single object) ----------------- #
    assert ijson is not None  # for type‑checkers

    first = _root_char(path)
    if first == "[":  # top‑level array
        for i, rec in enumerate(_stream_array(path)):
            if (txt := _extract_text(rec)):
                yield Document(txt, metadata={"source": str(path), "page": i})
    elif first == "{":  # top‑level *map* (possibly huge)
        if mode is _Mode.SMALL:
            # ↪ legacy small‑file path – keep previous eager behaviour
            obj = json.loads(path.read_text(encoding="utf‑8"))
            if (txt := _extract_text(obj)):
                yield Document(txt, metadata={"source": str(path), "page": 0})
        else:
            # ↪ **new** streaming path – one sub‑record at a time
            yield from _stream_object(path)
    else:  # malformed or exotic JSON
        raise json.JSONDecodeError("Unsupported JSON structure", doc="", pos=0)


def _parse_text(path: Path) -> Iterator[Document]:
    txt = path.read_text(encoding="utf‑8", errors="ignore")
    if txt.strip():
        yield Document(txt, metadata={"source": str(path.resolve())})


# Dispatch table – *every* accepted extension must appear exactly once.
_PARSERS: dict[str, Callable[[Path], Iterator[Document]]] = {
    ".jsonl": _parse_jsonl,
    ".ndjson": _parse_jsonl,
    ".json": _parse_json,
    ".txt": _parse_text,
    ".md": _parse_text,
    ".markdown": _parse_text,
}

_ALLOWED_EXTS = ", ".join(sorted(_PARSERS))

# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #
def load_documents(pattern: str) -> List[Document]:
    """
    Expand *pattern* into files and parse each into LangChain ``Document``\\s.

    Unsupported extensions raise ``ValueError`` so the CLI can show a helpful
    ❌ message.  IO/parsing errors are logged and skipped.
    """
    docs: list[Document] = []

    for file_path in _iter_files(pattern):
        if file_path.is_dir():
            continue

        ext = file_path.suffix.lower()
        parser = _PARSERS.get(ext)
        if not parser:
            raise ValueError(
                f"{ext!r} is not supported. Accepted: {_ALLOWED_EXTS}. "
                "For PDFs / DOCX run `ingen document-processing extract` and "
                "feed the resulting JSON/ND‑JSON into `ingen chunk run`."
            )

        try:
            docs.extend(parser(file_path))
        except (OSError, json.JSONDecodeError, jsonlines.Error, RuntimeError) as exc:
            # RuntimeError covers the "large JSON but no ijson" path
            print(f"[load_documents] Warning: {file_path} skipped ({exc})")

    if not docs:
        raise FileNotFoundError(f"No parsable documents found for {pattern!r}")

    return docs
