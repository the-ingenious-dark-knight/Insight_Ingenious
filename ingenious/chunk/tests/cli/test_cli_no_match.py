from typer.testing import CliRunner
from ingenious.chunk.cli import cli

def test_cli_no_matching_files(tmp_path):
    """`ingen chunk run` should exit 1 with a friendly ❌ when nothing matches."""
    pattern = tmp_path / "*.doesnotexist"
    res = CliRunner().invoke(cli, ["run", str(pattern)])
    assert res.exit_code == 1
    assert "❌" in res.output
    assert "No parsable documents found" in res.output
