# 🧠 Insight Ingenious – Document Chunking

A robust, extensible service **and** CLI for splitting documents into precise, context‑aware chunks—perfect for Retrieval‑Augmented Generation (RAG) pipelines.

---

## Overview

The **`chunk`** module provides the core text‑splitting capabilities within the Insight Ingenious framework. It transforms large source documents (Text, Markdown, JSON, JSONL) into smaller segments that balance semantic coherence with Large Language Model token limits.

**Ideal for:**

* Preparing data for vector databases and embedding models.
* Consistent, token‑aware splitting across mixed document types.
* Bidirectional context overlap between chunks to boost retrieval quality.

---

## Features

* ✨ **Multiple Strategies** – recursive, markdown, token, and semantic splitting.
* 📏 **Precise Budgeting** – configure `chunk_size` & `chunk_overlap` in tokens (via *tiktoken*) **or** characters.
* 🔗 **Bidirectional Overlap** – overlap before *and* after each chunk for maximum context preservation.
* 🌍 **Unicode Safe** – token strategy respects grapheme boundaries, protecting complex characters & emojis.
* 🧠 **Semantic Splitting** – OpenAI / Azure OpenAI embeddings find natural semantic breaks.
* ⚡ **Efficient Loading** – streams large JSON via *ijson* to minimise memory.
* 🆔 **Stable IDs** – deterministic, globally‑unique chunk IDs with configurable path encoding.

---

## Installation

The chunking capabilities are an **optional extra**.

```bash
# Install the core ingenious package with the chunking extra
uv pip install -e ".[chunk]"
```

> **Note**  Semantic splitting requires access to OpenAI or Azure OpenAI embeddings.

---

## Quick Start (CLI)

The primary entry‑point is `ingen chunk run`.

### Basic Recursive Splitting

Split a text file into 512‑token chunks with a 64‑token overlap:

```bash
ingen chunk run my_document.txt \
  --strategy recursive \
  --chunk-size 512 \
  --chunk-overlap 64 \
  --output chunks.jsonl
```

### Processing JSONL Input

Chunk each record from a JSON Lines file (e.g. output from *ingen document‑processing*):

```bash
ingen chunk run extracted_pages.jsonl -o chunks.jsonl
```

### Semantic Splitting *(requires `OPENAI_API_KEY`)*

```bash
ingen chunk run research_paper.md --strategy semantic -o semantic_chunks.jsonl
```

---

## Python API

```python
from ingenious.chunk import ChunkConfig, build_splitter

# 1 · Define configuration
config = ChunkConfig(
    strategy="token",
    chunk_size=256,
    chunk_overlap=32,
    overlap_unit="tokens"
)

# 2 · Build the splitter instance
splitter = build_splitter(config)

# 3 · Split text
text = "Your long document content goes here..."
chunks = splitter.split_text(text)

print(f"Generated {len(chunks)} chunks.")
# print(chunks[0])
```

---

## Configuration & Strategies

Behaviour is controlled via CLI flags that map 1‑to‑1 with the `ChunkConfig` model.

### Available Strategies

| Strategy    | Description                                                        | Key Configuration                                                        |
| ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `recursive` | Hierarchical splits (paragraph→sentence→word). Fast and versatile. | `--chunk-size`, `--chunk-overlap`, `--separators`                        |
| `markdown`  | Aware of Markdown structure (headers, lists).                      | `--chunk-size`, `--chunk-overlap`                                        |
| `token`     | Splits on token boundaries, Unicode‑safe.                          | `--chunk-size`, `--chunk-overlap`, `--encoding-name`                     |
| `semantic`  | Uses embeddings to split at semantic breaks.                       | `--embed-model`, `--azure-deployment`, `--semantic-threshold-percentile` |

### Core Options

| Flag              | Description                                      | Default       |
| ----------------- | ------------------------------------------------ | ------------- |
| `--strategy`      | Splitting algorithm.                             | `recursive`   |
| `--chunk-size`    | Max size of each chunk (tokens/chars).           | `1024`        |
| `--chunk-overlap` | Overlap between adjacent chunks.                 | `128`         |
| `--overlap-unit`  | Unit for size/overlap: `tokens` or `characters`. | `tokens`      |
| `--encoding-name` | *tiktoken* encoding for token counting.          | `cl100k_base` |

---

## Input File Contract

| Format                     | Handling                                                                         |
| -------------------------- | -------------------------------------------------------------------------------- |
| `.txt`, `.md`, `.markdown` | Entire file treated as one document.                                             |
| `.json`                    | Object or array; each object must include `text`, `page_content`, **or** `body`. |
| `.jsonl`, `.ndjson`        | One JSON object per line with the keys above.                                    |

---

## Advanced · Stable Chunk IDs

CLI generates deterministic IDs: `<prefix>#p<page>.<pos>-<hash>` where `<prefix>` is set by `--id-path-mode`.

* **`rel`** *(default)* – path relative to CWD (or `--id-base`). Falls back to hashed abs‑path when outside base.
* **`hash`** – always truncated SHA‑256 of abs‑path. Good for privacy / cross‑machine stability.
* **`abs`** – absolute file system path (may leak info). Requires `--force-abs-path`.

```bash
# Example: use hashing for the ID prefix
ingen chunk run my_document.txt --id-path-mode hash
```

---

## Development & Testing

```bash
# Install testing dependencies
a uv pip install -e ".[chunk,test]"

# Run the test suite
pytest ingenious/chunk/tests
```

---

**Happy Chunking!** 🚀
