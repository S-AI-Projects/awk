import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = Path("exercises/practice/pascals-triangle")
GENERATED_FILE = EXERCISE / "test-pascals-triangle.bats"

EVIDENCE = ROOT / "work/R06-T042/evidence"

EXPECTED_TESTS = [
    "zero rows",
    "single row",
    "two rows",
    "three rows",
    "four rows",
    "five rows",
    "six rows",
    "ten rows",
    "two triangles",
]


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def version(command):
    result = subprocess.run(
        command, capture_output=True, text=True
    )
    return (result.stdout or result.stderr).splitlines()[0]


def prepare_copy(destination):
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            ".git", "work", "__pycache__", ".DS_Store"
        ),
    )


def generate_tests(repository):
    result = subprocess.run(
        ["bin/generate_tests", "--no-pull", "pascals-triangle"],
        cwd=repository,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        fail("Generation failed:\n" + result.stdout + result.stderr)

    generated = repository / GENERATED_FILE

    if not generated.is_file():
        fail("Generated Bats file is missing.")

    content = generated.read_text()

    test_names = re.findall(
        r'^\s*@test\s+"([^"]+)"',
        content,
        re.MULTILINE,
    )

    if test_names != EXPECTED_TESTS:
        fail(
            f"Expected tests: {EXPECTED_TESTS}\n"
            f"Actual tests: {test_names}"
        )

    normalized = [
        line for line in content.splitlines()
        if not re.match(r"^\s*# generated on ", line)
    ]

    return content, normalized, test_names


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    inputs = EVIDENCE / "inputs"
    inputs.mkdir(exist_ok=True)

    # Preserve the source files used for generation and validation.
    source_files = [
        ".meta/config.json",
        ".meta/tests.toml",
        ".meta/template.j2",
        ".meta/example.awk",
        ".docs/instructions.md",
    ]

    for relative in source_files:
        source = ROOT / EXERCISE / relative
        destination = inputs / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    canonical = (
        Path.home()
        / ".cache/exercism/configlet/problem-specifications"
        / "exercises/pascals-triangle/canonical-data.json"
    )

    if not canonical.is_file():
        fail("Canonical problem specifications are missing.")

    shutil.copy2(canonical, inputs / "canonical-data.json")

    print("Creating two fresh repository copies...")

    with tempfile.TemporaryDirectory(
        prefix="r06-t042-generation-"
    ) as temporary:

        temporary = Path(temporary)
        first = temporary / "run1"
        second = temporary / "run2"

        prepare_copy(first)
        prepare_copy(second)

        print("Generating tests in copy 1...")
        content1, normalized1, names1 = generate_tests(first)

        print("Generating tests in copy 2...")
        content2, normalized2, names2 = generate_tests(second)

        (EVIDENCE / "generated-run1.bats").write_text(content1)
        (EVIDENCE / "generated-run2.bats").write_text(content2)

        if normalized1 != normalized2:
            fail("Generated files differ after timestamp normalization.")

        if names1 != names2:
            fail("Test names differ between generations.")

    (EVIDENCE / "expected-test-cases.txt").write_text(
        "\n".join(EXPECTED_TESTS) + "\n"
    )

    versions = {
        "Python": ["python3", "--version"],
        "GNU Awk": ["gawk", "--version"],
        "Bats": ["bats", "--version"],
        "Bash": ["bash", "--version"],
        "jq": ["jq", "--version"],
        "Git": ["git", "--version"],
    }

    with (EVIDENCE / "environment.txt").open("w") as file:
        for name, command in versions.items():
            try:
                file.write(f"{name}: {version(command)}\n")
            except (FileNotFoundError, IndexError):
                file.write(f"{name}: unavailable\n")

        result = subprocess.run(
            ["python3", "-c",
             "import jinja2; print(jinja2.__version__)"],
            capture_output=True, text=True
        )
        file.write(
            "Jinja2: " +
            (result.stdout.strip() or "unavailable") + "\n"
        )

    report = (
        "Reproducibility check: PASS\n"
        "Fresh repository copies: 2\n"
        "Timestamp normalization: generated timestamp line removed\n"
        "Other generated-file differences: none\n"
        f"Expected test count: {len(EXPECTED_TESTS)}\n"
        f"Actual test count: {len(names1)}\n"
        "All expected test cases present: PASS\n"
    )

    (EVIDENCE / "regeneration-results.txt").write_text(report)

    print()
    print("PASS: Both generations match after timestamp normalization.")
    print(f"PASS: All {len(names1)} expected tests are present.")
    print(f"Evidence saved in: {EVIDENCE}")


if __name__ == "__main__":
    main()
