
# Pascal's Triangle — Test Generation

## Purpose

This document explains how the Pascal's Triangle Bats tests are generated and how to reproduce them.

## Source files

The generated test file is:

`exercises/practice/pascals-triangle/test-pascals-triangle.bats`

It is generated using these inputs:

- `.meta/tests.toml` — selects the canonical test cases.
- `.meta/template.j2` — defines how the Bats tests are rendered.
- `canonical-data.json` — contains the canonical test cases from the Exercism problem-specifications repository.

The canonical data is located at:

`~/.cache/exercism/configlet/problem-specifications/exercises/pascals-triangle/canonical-data.json`

The exercise's `.meta/config.json` identifies the learner solution, test file and reference implementation.

## Test case mapping

The eight canonical cases selected by `.meta/tests.toml` are:

| Case | Description |
|---|---|
| 9920ce55-9629-46d5-85d6-4201f4a4234d | zero rows |
| 70d643ce-a46d-4e93-af58-12d88dd01f21 | single row |
| a6e5a2a2-fc9a-4b47-9f4f-ed9ad9fbe4bd | two rows |
| 97206a99-79ba-4b04-b1c5-3c0fa1e16925 | three rows |
| 565a0431-c797-417c-a2c8-2935e01ce306 | four rows |
| 06f9ea50-9f51-4eb2-b9a9-c00975686c27 | five rows |
| c3912965-ddb4-46a9-848e-3363e6b00b13 | six rows |
| 6cb26c66-7b57-4161-962c-81ec8c99f16b | ten rows |

The template also defines an additional `two triangles` test. Therefore, the generated Bats file contains nine tests in total.

## Regeneration command

From the repository root, run:

```bash
bin/generate_tests --no-pull pascals-triangle
```

The `--no-pull` option prevents the generator from pulling updates to the problem-specifications repository. It uses the locally available canonical data.

## Reproducibility

Two fresh repository copies were generated independently.

After removing the generated timestamp line, both generated test files were identical.

Both files contained nine tests, with no other differences.

## Validation

The reference implementation is `.meta/example.awk`.

The validation checker:

```bash
python3 work/R06-T042/check.py
```

copies the exercise, substitutes the reference implementation only in the temporary copy, and runs `bin/validate_one_exercise`.

The validation completed successfully:

- Nine tests executed.
- All nine tests passed.
- Validator exited successfully.
- Original learner solution remained unchanged.
