"""Shared isolated validation helper for the R06 course checks."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def validate_reference(repo: Path, slug: str) -> tuple[str, int]:
    exercise = repo / "exercises" / "practice" / slug
    config = json.loads((exercise / ".meta/config.json").read_text())
    files = config["files"]
    solution = exercise / files["solution"][0]
    test = exercise / files["test"][0]
    example = exercise / files.get("example", files.get("exemplar"))[0]
    for path in (solution, test, example):
        if not path.is_file() or not path.resolve().is_relative_to(exercise.resolve()):
            raise AssertionError(f"Invalid configured exercise path: {path}")

    with tempfile.TemporaryDirectory(prefix=f"r06-{slug}-") as scratch:
        scratch_root = Path(scratch)
        copied = scratch_root / slug
        shutil.copytree(exercise, copied, dirs_exist_ok=True)
        copied_solution = copied / files["solution"][0]
        shutil.copy2(copied / files.get("example", files.get("exemplar"))[0], copied_solution)
        proc = subprocess.run(
            [str(repo / "bin/validate_one_exercise"), str(copied)],
            cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if proc.returncode:
            raise AssertionError(f"reference validator exited {proc.returncode}:\n{proc.stdout}")
        match = re.search(r"(?m)^1\.\.(\d+)\s*$", proc.stdout)
        if not match or int(match.group(1)) == 0:
            raise AssertionError(f"validator reported no executed tests:\n{proc.stdout}")
        return proc.stdout, int(match.group(1))
