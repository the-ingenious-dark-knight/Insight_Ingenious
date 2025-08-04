"""
Ingenious Chunking CLI
======================

Usage example::

    ingen chunk run test_files/pages_azdocint_pdf_scanned.jsonl \
        --strategy recursive --chunk-size 64 --chunk-overlap 24 \
        --output azdocint_chunks.jsonl
"""

from __future__ import annotations

import hashlib
import pathlib

# ── std‑lib ────────────────────────────────────────────────────────────────
from collections import defaultdict
from enum import Enum
from typing import Iterable

# ── third‑party ────────────────────────────────────────────────────────────
import jsonlines
import typer
from pydantic import ValidationError

# ── first‑party (this package) ─────────────────────────────────────────────
from ingenious.chunk.utils.id_path import _norm_source

from .config import ChunkConfig
from .factory import build_splitter
from .loader import load_documents


# --------------------------------------------------------------------------- #
# Resolve OpenAI base error class across client versions                      #
# --------------------------------------------------------------------------- #
def _resolve_openai_error() -> type[BaseException]:
    """
    Return the canonical ``OpenAIError`` class, compatible with both
    *openai < 1.0* (``openai.error.OpenAIError``) **and** *≥ 1.0*
    (``openai.OpenAIError``).
    """
    try:
        import openai  # type: ignore

        for attr in ("OpenAIError", "error"):
            candidate = getattr(openai, attr, None)
            # <1.0> stores it in sub‑module ``openai.error``
            if candidate and isinstance(candidate, type):
                return candidate  # ≥ 1.0 path
            if candidate and hasattr(candidate, "OpenAIError"):
                return candidate.OpenAIError  # < 1.0 path
    except ModuleNotFoundError:  # pragma: no cover
        pass

    # Fallback shim keeps type‑checking happy
    class _Fallback(Exception):  # type: ignore
        pass

    return _Fallback


_OpenAIError = _resolve_openai_error()

try:
    from azure.core.exceptions import HttpResponseError
except ModuleNotFoundError:  # package not installed

    class HttpResponseError(Exception):  # type: ignore
        pass


_EXPECTED_SPLITTER_ERRORS: tuple[type[BaseException], ...] = (
    ValueError,
    RuntimeError,
    _OpenAIError,  # covers public + Azure OpenAI
    HttpResponseError,  # covers direct Azure SDK calls (optional)
)


# --------------------------------------------------------------------------- #
# Enum with the allowed strategies                                            #
# --------------------------------------------------------------------------- #
class Strategy(str, Enum):
    recursive = "recursive"
    markdown = "markdown"
    token = "token"
    semantic = "semantic"


# --------------------------------------------------------------------------- #
# Shared “input‑file contract” text                                           #
# --------------------------------------------------------------------------- #
_CONTRACT = (
    "[bold]Input‑file contract[/bold]\n"
    "• .txt / .md / .markdown – entire file becomes one document\n"
    "• .json       – an OBJECT or ARRAY of objects; each object must have a\n"
    "                  'text' | 'page_content' | 'body' key containing the page text\n"
    "• .jsonl / .ndjson – **one object per line** with the same keys above"
)


def _safe_load(pattern: str):
    """
    Wrapper around :pyfunc:`ingenious.chunk.loader.load_documents` that converts
    loader‑level errors into a consistent, user‑friendly CLI failure.

    Raises
    ------
    typer.Exit
        Always exits with code 1 after showing a coloured ❌ banner when **any**
        of the following bubble up:

        • ``ValueError`` – unsupported file type (e.g. PDF)
        • ``FileNotFoundError`` – pattern matches zero parseable files
        • ``RuntimeError`` – fatal loader error (e.g. ijson missing)
        • ``HttpResponseError`` – remote‑storage HTTP failure (Azure SDK)
    """
    try:
        return load_documents(pattern)
    except (ValueError, FileNotFoundError, RuntimeError, HttpResponseError) as exc:
        typer.secho(f"❌  {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


# --------------------------------------------------------------------------- #
# Typer app                                                                   #
# --------------------------------------------------------------------------- #
cli = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
    help=f"Split files into chunked JSONL for RAG pipelines.\n\n{_CONTRACT}",
)


# --------------------------------------------------------------------------- #
# Root callback – nothing to do, but keeps Typer happy                        #
# --------------------------------------------------------------------------- #
@cli.callback(invoke_without_command=True, no_args_is_help=True)
def main() -> None:  # pragma: no cover
    """See sub‑commands for usage."""
    # No body required


# --------------------------------------------------------------------------- #
# `run` sub‑command                                                           #
# --------------------------------------------------------------------------- #
@cli.command(
    "run",
    help=f"Chunk files and write a JSONL output file.\n\n{_CONTRACT}",
)
def run(  # noqa: PLR0913 – many CLI knobs by design
    # -------------- positional input ------------------------------------
    path: str = typer.Argument(
        ...,
        metavar="PATH",
        help="File, directory, or glob pattern",
        rich_help_panel="Input‑file contract",
    ),
    # -------------- core knobs ------------------------------------------
    strategy: Strategy = typer.Option(
        Strategy.recursive,
        "--strategy",
        "-s",
        help="Chunking strategy to use.",
    ),
    chunk_size: int = typer.Option(
        1024, "--chunk-size", help="Max tokens/characters per chunk"
    ),
    chunk_overlap: int = typer.Option(
        128, "--chunk-overlap", help="Overlap between chunks (< size)"
    ),
    overlap_unit: str = typer.Option(
        "tokens",
        "--overlap-unit",
        help="Unit for overlap window: tokens | characters",
        rich_help_panel="Advanced",
    ),
    # -------------- advanced knobs --------------------------------------
    separators: str = typer.Option(
        "", help="Custom separators (join with '|') for recursive splitter"
    ),
    encoding_name: str = typer.Option(
        "cl100k_base", help="Tokenizer encoding for token splitter"
    ),
    embed_model: str = typer.Option("", help="Embedding model for semantic splitter"),
    azure_deployment: str = typer.Option(
        "", help="Azure OpenAI deployment for semantic splitter"
    ),
    semantic_threshold_percentile: int = typer.Option(
        95, help="Similarity percentile threshold for semantic splitter (0-100)"
    ),
    # -------------- ID‑path handling ------------------------------------
    id_path_mode: str = typer.Option(
        "rel",
        "--id-path-mode",
        help=(
            "Encode source paths inside chunk IDs: rel | hash | abs.\n\n"
            "⚠️  Using 'abs' will embed your *full* filesystem path into every "
            "chunk ID.  You must supply --force-abs-path to acknowledge this "
            "risk."
        ),
        rich_help_panel="Output",
    ),
    id_base: str = typer.Option(
        "",
        "--id-base",
        help="Base directory for --id-path-mode=rel (defaults to CWD)",
        rich_help_panel="Output",
    ),
    # NOTE: default bumped to 64 bits → 16 hex chars
    id_hash_bits: int = typer.Option(
        64,
        "--id-hash-bits",
        help="Bits to keep from the SHA‑256 hash used in chunk IDs "
        "(multiple of 4; ≥ 32, ≤ 256).  Default: 64 bits → 16 hex.",
        rich_help_panel="Output",
    ),
    # -------------- safety acknowledgement --------------------------------
    force_abs_path: bool = typer.Option(
        False,
        "--force-abs-path",
        help=(
            "⚠️  REQUIRED when --id-path-mode=abs. Confirms you understand "
            "absolute source paths will be embedded in every chunk ID and "
            "may leak sensitive information when the file is shared."
        ),
        rich_help_panel="Output",
    ),
    # -------------- output ----------------------------------------------
    output: str = typer.Option(
        "chunks.jsonl", "--output", "-o", help="Output JSONL filepath"
    ),
    # -------------- diagnostics ------------------------------------------
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show full Python traceback on internal errors.",
        rich_help_panel="Debugging",
    ),
) -> None:
    """Read files, split into chunks, and write them as JSONL."""

    # ------------------------------------------------------------------ #
    # Guard against accidental PII leakage                                 #
    # ------------------------------------------------------------------ #
    if id_path_mode == "abs" and not force_abs_path:
        typer.secho(
            "❌  --id-path-mode=abs embeds *absolute* filesystem paths in "
            "chunk IDs which can reveal sensitive information.\n"
            "   Re‑run with --force-abs-path if you really want this.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # ------------------------------------------------------------------ #
    # Build config & splitter                                              #
    # ------------------------------------------------------------------ #
    try:
        cfg = ChunkConfig(
            strategy=strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            overlap_unit=overlap_unit,
            separators=separators.split("|") if separators else None,
            encoding_name=encoding_name,
            embed_model=embed_model or None,
            azure_openai_deployment=azure_deployment or None,
            semantic_threshold_percentile=semantic_threshold_percentile,  # Pass new param
            id_path_mode=id_path_mode,
            id_base=pathlib.Path(id_base) if id_base else None,
            id_hash_bits=id_hash_bits,
        )
    except ValidationError as exc:
        # Uniform UX: red ❌ prefix + graceful exit on user‑config errors
        typer.secho(f"❌  {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    splitter = build_splitter(cfg)

    # ------------------------------------------------------------------ #
    # Load documents                                                       #
    # ------------------------------------------------------------------ #
    docs = _safe_load(path)

    # ------------------------------------------------------------------ #
    # Prepare output path                                                  #
    # ------------------------------------------------------------------ #
    out_path = pathlib.Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Chunk                                                                #
    # ------------------------------------------------------------------ #
    try:
        chunks = splitter.split_documents(docs)
    except _EXPECTED_SPLITTER_ERRORS as exc:
        # ── Expected, user‑visible failure ────────────────────────────── #
        typer.secho(f"❌  Chunking failed: {exc}", fg=typer.colors.RED)

        # `--verbose / -v` ⇒ surface the full traceback for diagnostics.
        if verbose:
            import sys
            import traceback

            traceback.print_exc(file=sys.stderr)

        # Graceful termination with exit‑code 1 (same UX as loader errors)
        raise typer.Exit(code=1) from exc

    # ------------------------------------------------------------------ #
    # Unexpected internal error – present a friendly banner and exit 1   #
    # unless the user asked for a full traceback via --verbose.          #
    # ------------------------------------------------------------------ #
    except Exception as exc:  # pragma: no cover
        typer.secho(f"❌  {exc}", fg=typer.colors.RED)

        if verbose:
            import sys
            import traceback

            traceback.print_exc(file=sys.stderr)

        # Graceful termination, mirroring _safe_load behaviour
        raise typer.Exit(code=1) from exc

    # ------------------------------------------------------------------ #
    # Write                                                                #
    # ------------------------------------------------------------------ #
    try:
        _write_chunks_jsonl(chunks, out_path, cfg)
        typer.secho(
            f"✅ Wrote {len(chunks)} chunks → {out_path}",
            fg=typer.colors.GREEN,
        )
    except (OSError, jsonlines.Error) as exc:  # pragma: no cover
        typer.secho(
            f"❌  Failed to write output file: {exc}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1) from exc


# --------------------------------------------------------------------------- #
# Helper – primitives                                                         #
# --------------------------------------------------------------------------- #
_PRIMITIVE = (str, int, float, bool, type(None))


def _json_safe(val, *, max_depth: int = 50):
    """
    Convert *val* into a JSON‑serialisable structure **iteratively**
    while detecting *true* reference cycles.

    Key points
    ----------
    • **Cycle detection** Uses an *on‑path* set instead of a global
      “visited” set—objects are marked only while their branch is being
      explored, so legitimate shared references do **not** trigger
      “[Circular Reference]”.
    • **Depth guard** Branches deeper than *max_depth* are stringified.
    • **Containers**
      dict   ⇒ dict (keys cast to ``str``)
      list/tuple/set ⇒ list (sets are sorted for determinism)
    • **Primitives / fallback** Unchanged from previous behaviour.
    """
    if isinstance(val, _PRIMITIVE):
        return val

    # Stack frame: (obj, depth, parent_container, parent_key, entered_flag)
    stack: list[tuple[object, int, object | None, object | None, bool]] = [
        (val, 0, None, None, False)
    ]
    root_out: object | None = None
    on_path: set[int] = set()  # IDs of objects currently being explored

    while stack:
        cur, depth, parent, key, entered = stack.pop()
        obj_id = id(cur)

        # ── Second visit ⇒ finished exploring children ────────────────────
        if entered:
            on_path.discard(obj_id)
            continue

        # ── Handle primitives & depth guard up‑front ──────────────────────
        if depth >= max_depth or isinstance(cur, _PRIMITIVE):
            converted = cur if isinstance(cur, _PRIMITIVE) else str(cur)
            if parent is None:
                root_out = converted
            else:
                if isinstance(parent, dict):
                    parent[key] = converted  # type: ignore[index-assignment]
                else:  # parent is list surrogate
                    parent.insert(0, converted)
            continue

        # ── True cycle detected ───────────────────────────────────────────
        if obj_id in on_path:
            converted = "[Circular Reference]"
            if parent is None:
                root_out = converted
            else:
                if isinstance(parent, dict):
                    parent[key] = converted
                else:
                    parent.insert(0, converted)
            continue

        # ── First time we see this composite object ───────────────────────
        on_path.add(obj_id)

        if isinstance(cur, dict):
            container: dict = {}
            # Attach placeholder to parent before pushing children
            if parent is None:
                root_out = container
            else:
                if isinstance(parent, dict):
                    parent[key] = container
                else:
                    parent.insert(0, container)

            # Re‑visit current node after its children
            stack.append((cur, depth, parent, key, True))

            # Push children in reverse to preserve order
            for k, v in reversed(list(cur.items())):
                stack.append((v, depth + 1, container, str(k), False))

        elif isinstance(cur, (list, tuple, set)):
            container: list = []
            if parent is None:
                root_out = container
            else:
                if isinstance(parent, dict):
                    parent[key] = container
                else:
                    parent.insert(0, container)

            stack.append((cur, depth, parent, key, True))

            # For deterministic output, sort sets by str(); lists/tuples keep order
            items = sorted(cur, key=str) if isinstance(cur, set) else list(cur)
            for item in reversed(items):
                stack.append((item, depth + 1, container, None, False))
        else:
            # Fallback – stringify unsupported container types
            converted = str(cur)
            if parent is None:
                root_out = converted
            else:
                if isinstance(parent, dict):
                    parent[key] = converted
                else:
                    parent.insert(0, converted)

    # mypy guard – root_out is always assigned
    assert root_out is not None, "root_out should have been initialised"
    return root_out


def _write_chunks_jsonl(
    chunks: Iterable,
    out_path: pathlib.Path,
    cfg: ChunkConfig,
) -> None:
    """
    Persist *chunks* to *out_path* in deterministic‑ID JSONL format.

    • ID format:  ``<abs‑src>#p<page>.<pos>-<hashN>``
      – *abs‑src* : absolute, POSIX‑style source path (portable)
      – *page* : zero‑based page index from metadata (default 0)
      – *pos* : deterministic ordinal of the chunk within that page
      – *hashN* : first *N/4* hex chars of **SHA‑256(page_content)** where
        *N = cfg.id_hash_bits* (default 48 bits → 12 hex)

    The scheme stays **stable across reruns** yet guarantees uniqueness even
    when two chunks share identical text.
    """
    # Counter keyed by (source_path, page) → next position integer
    position_ctr: defaultdict[tuple[str, int], int] = defaultdict(int)

    with jsonlines.open(out_path, mode="w") as writer:
        for chunk in chunks:
            # 1️⃣ Normalised source path
            src_path = _norm_source(chunk.metadata.get("source", ""), cfg)

            # 2️⃣ Page number
            page = int(chunk.metadata.get("page", 0))

            # 3️⃣ Per‑page deterministic position
            pos = position_ctr[(src_path, page)]
            position_ctr[(src_path, page)] += 1

            # 4️⃣ Content hash (length derived from cfg)
            hex_len = cfg.id_hash_bits // 4
            digest = hashlib.sha256(
                chunk.page_content.encode("utf-8", "surrogatepass")
            ).hexdigest()[:hex_len]

            # 5️⃣ Stable, globally‑unique ID
            chunk_id = f"{src_path}#p{page}.{pos}-{digest}"

            writer.write(
                {
                    "id": chunk_id,
                    "text": chunk.page_content,
                    "meta": _json_safe(chunk.metadata),
                }
            )
