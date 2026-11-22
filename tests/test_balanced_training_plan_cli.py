from pathlib import Path
import subprocess
import sys


def test_balanced_training_planner_cli_imports_from_repo_root():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/build_balanced_training_plan.py", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--manifests-dir" in result.stdout
    assert "No module named 'src'" not in result.stderr
