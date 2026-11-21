#!/usr/bin/env python3
"""Validate rectangles file-role paths from exercise metadata."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EX=ROOT/"exercises/practice/rectangles"

def validate_files(exercise: Path, config: dict) -> dict[str,list[Path]]:
    files=config.get("files")
    if not isinstance(files,dict) or not files:
        raise ValueError("files must be a non-empty object")
    resolved={}
    base=exercise.resolve()
    for role,names in files.items():
        if not isinstance(names,list) or not names:
            raise ValueError(f"{role} must contain at least one path")
        paths=[]
        for name in names:
            rel=Path(name)
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"path outside exercise for {role}: {name}")
            path=(exercise/rel).resolve()
            if not path.is_relative_to(base):
                raise ValueError(f"path outside exercise for {role}: {name}")
            if not path.is_file():
                raise ValueError(f"missing {role} file: {name}")
            paths.append(path)
        resolved[role]=paths
    for required in ("solution","test","example"):
        if required not in resolved:
            raise ValueError(f"missing required role: {required}")
    return resolved

def main() -> None:
    config=json.loads((EX/".meta/config.json").read_text())
    roles=validate_files(EX,config)
    assert roles["solution"][0].name=="rectangles.awk"
    assert roles["test"][0].name=="test-rectangles.bats"
    assert roles["example"][0].name=="example.awk"
    print("PASS: solution, test, example, and all declared files resolve inside rectangles")

if __name__ == "__main__":
    main()
