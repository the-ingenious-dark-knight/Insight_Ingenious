"""Insight Ingenious – selective‑source tests for :pyfunc:`_iter_sources`
========================================================================
``_iter_sources`` converts *CLI arguments* (paths or URLs) into a stream of
``(label, src)`` pairs consumed by the document‑processing command.  This
module ensures the helper **filters out non‑PDF inputs** when it is given a
*directory* argument.  A naïve rglob could yield ``.txt`` or other files –
the test verifies that only the expected PDF appears in the iterator.

The happy‑path behaviour of ``_iter_sources`` (single file, nested paths,
URLs, etc.) is covered in *test_cli.py*; edge conditions (404s, empty
folders) are handled in *test_iter_sources_edge.py*.  Here we focus solely
on the **filtering logic**.
"""

from __future__ import annotations

from pathlib import Path

from ingenious.document_processing.cli import _iter_sources

# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #


def test_iter_sources_skips_non_pdf(tmp_path: Path, pdf_path: Path) -> None:
    """Iterator must ignore non‑PDF files when traversing a directory.

    Parameters
    ----------
    tmp_path : Path
        *pytest* built‑in fixture – provides an isolated temporary
        directory unique to the test invocation.
    pdf_path : Path
        Custom fixture defined at project level supplying a **valid** sample
        PDF.  The file is copied into *tmp_path* to mimic the user pointing
        the CLI at a folder containing multiple files.

    Test steps
    ~~~~~~~~~~
    1.  Create a *dummy* text file (``note.txt``) inside *tmp_path*.
    2.  Copy the sample PDF into the same directory.
    3.  Invoke :pyfunc:`_iter_sources` with the folder path.
    4.  Collect the *labels* (first element of each tuple).
    5.  Assert that **only** the PDF label appears – the ``.txt`` must be
        absent – proving the helper correctly filters for PDF inputs.

    The function makes no assertions about the *src* component; that is
    tested elsewhere.  Here we merely validate *selection* criteria.
    """

    # ─── Arrange – create a non‑PDF noise file ───────────────────────────────
    (tmp_path / "note.txt").write_text("ignore me")

    # Copy the valid sample PDF alongside it
    dst = tmp_path / pdf_path.name
    dst.write_bytes(pdf_path.read_bytes())

    # ─── Act – iterate sources in directory ─────────────────────────────────
    labels = [label for label, _ in _iter_sources(tmp_path)]

    # ─── Assert – .txt skipped, .pdf present ────────────────────────────────
    assert str(dst) in labels, "Expected PDF file missing from iterator"
    assert not any("note.txt" in lbl for lbl in labels), (
        "Non‑PDF file should be filtered out"
    )
