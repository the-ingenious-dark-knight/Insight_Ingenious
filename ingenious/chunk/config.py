# ingenious/chunk/config.py
import warnings
from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkConfig(BaseModel):
    """
    User-facing configuration for content chunking.

    * Mirrors CLI arguments 1-1.
    * The model is **frozen** (immutable) so invariants cannot be broken after
      instantiation.
    """

    # ------------------------------------------------------------------
    # Pydantic model settings
    # ------------------------------------------------------------------
    model_config = ConfigDict(frozen=True)

    # ------------------------------------------------------------------
    # Strategy selector
    # ------------------------------------------------------------------
    strategy: Literal["recursive", "markdown", "token", "semantic"] = "recursive"

    id_path_mode: Literal["abs", "rel", "hash"] = "rel"
    id_base: Path | None = Field(
        default=None, description="Base dir for relative ID paths"
    )

    # ------------------------------------------------------------------
    # Digest truncation – collision domain
    # ------------------------------------------------------------------
    id_hash_bits: int = Field(
        64,
        ge=32,
        le=256,
        description=(
            "Number of **SHA‑256 bits** kept when truncating the hexadecimal "
            "digest that forms a chunk‑ or path‑hash.  Must be a multiple of 4 "
            "(1 hex digit = 4 bits)."
        ),
    )

    # ------------------------------------------------------------------
    # Shared knobs
    # ------------------------------------------------------------------
    chunk_size: int = Field(
        1024,
        ge=1,
        description="Max tokens/characters allowed in a single chunk. NOTE: This is ignored by the 'semantic' strategy.",
    )
    chunk_overlap: int = Field(
        128,
        ge=0,
        description="Number of tokens/characters shared between consecutive chunks.",
    )

    overlap_unit: Literal["tokens", "characters"] = "tokens"

    # ------------------------------------------------------------------
    # Strategy-specific options
    # ------------------------------------------------------------------
    # recursive / markdown
    separators: List[str] | None = None

    # token splitter
    encoding_name: str = "cl100k_base"

    # semantic splitter
    embed_model: str | None = None
    azure_openai_deployment: str | None = None
    semantic_threshold_percentile: int = Field(
        95,
        ge=0,
        le=100,
        description="The percentile of similarity scores to use as a threshold for splitting chunks in the 'semantic' strategy.",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_hash_bits(self):
        if self.id_hash_bits % 4 != 0:
            raise ValueError("id_hash_bits must be a multiple of 4")
        return self

    @model_validator(mode="after")
    def _warn_small_hash_bits(self):
        if self.id_hash_bits < 48:
            warnings.warn(
                "id_hash_bits < 48 increases the probability of prefix "
                "collisions in large corpora. Consider using the default 64 "
                "or higher.",
                stacklevel=2,
            )
        return self

    @model_validator(mode="after")
    def _validate_id_mode(self):
        if self.id_path_mode == "rel":
            # Default base to CWD if not supplied
            object.__setattr__(self, "id_base", self.id_base or Path.cwd())
        else:
            # In abs/hash mode, id_base must not be set
            if self.id_base is not None:
                raise ValueError(
                    "id_base is only applicable when id_path_mode == 'rel'"
                )
        return self

    @model_validator(mode="after")
    def _validate_overlap(self):
        """
        Enforce ``chunk_overlap < chunk_size`` for non-semantic strategies.
        """
        # This validation does not apply to the semantic strategy, as chunk_size is not used for sizing.
        if self.strategy != "semantic" and self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be smaller than "
                f"chunk_size ({self.chunk_size})"
            )
        return self

    @model_validator(mode="after")
    def _validate_semantic_strategy(self):
        """
        Enforce constraints specific to the semantic strategy.
        """
        if self.strategy == "semantic" and self.overlap_unit == "characters":
            raise ValueError(
                "The 'semantic' strategy does not support 'characters' as an overlap_unit. "
                "Please use 'tokens' for semantic chunking."
            )
        return self

    @model_validator(mode="after")
    def _semantic_warn_backend(self):
        """
        Allow the semantic strategy to run when *neither* an Azure deployment
        nor an explicit embed model is supplied.  We fall back to the public
        OpenAI endpoint and emit a warning so users remember to set
        OPENAI_API_KEY.
        """
        if self.strategy == "semantic" and not (
            self.azure_openai_deployment or self.embed_model
        ):
            import warnings

            warnings.warn(
                "Semantic splitter: no `azure_openai_deployment` or "
                "`embed_model` supplied – falling back to the public "
                "OpenAI endpoint with model 'text-embedding-3-small'. "
                "Make sure OPENAI_API_KEY is set.",
                stacklevel=2,
            )
        return self
