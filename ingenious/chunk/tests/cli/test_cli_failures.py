from typer.testing import CliRunner

from ingenious.chunk.cli import cli


def test_cli_invalid_overlap(tmp_path):
    """CLI should fail fast when chunk_overlap == chunk_size (invalid)."""
    src = tmp_path / "doc.txt"
    src.write_text("hello")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["run", str(src), "--chunk-size", "10", "--chunk-overlap", "10"],
        catch_exceptions=True,
    )

    # --- assertions ---------------------------------------------------- #
    # The CLI should exit 1 with the red ❌ banner and *no* traceback.
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "❌" in result.output
