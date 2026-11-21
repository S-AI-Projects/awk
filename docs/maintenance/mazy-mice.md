# Mazy Mice — Test Generation Route & Maintenance

## 1. Overview & Context

- **Exercise**: `mazy-mice`
- **Track**: AWK (`S-AI-Projects/awk`)
- **Author**: `rabestro` (Jegors Čemisovs)
- **Task Reference**: `R06-T032`
- **Learner Solution Stub**: `exercises/practice/mazy-mice/mazy-mice.awk`
- **Reference Solution**: `exercises/practice/mazy-mice/.meta/example.awk`
- **Test Suite**: `exercises/practice/mazy-mice/test-mazy-mice.bats`
- **Maze Validator Helper**: `exercises/practice/mazy-mice/test-maze.awk`
- **Exercise Configuration**: `exercises/practice/mazy-mice/.meta/config.json`
- **Test Configuration**: `exercises/practice/mazy-mice/.meta/tests.toml`

The objective of `mazy-mice` is to generate perfect mazes of configurable dimensions ($2 \times \text{Cols} + 1$ by $2 \times \text{Rows} + 1$ characters) using box-drawing characters and entry/exit door arrows (`⇨`).

---

## 2. Generator Analysis & Maintained Test Source

In the Exercism AWK track repository, test generation is governed by `bin/generate_tests`:
- Exercises containing a Jinja2 template (`.meta/template.j2`) are dynamically rendered against the canonical specifications in `problem-specifications/exercises/<exercise>/canonical-data.json`, filtered by `.meta/tests.toml`.
- For `mazy-mice`, **no per-exercise Jinja template (`template.j2`) exists**.
- Furthermore, `mazy-mice` is a track-unique practice exercise authored specifically for the AWK track; it is not present in the upstream Exercism `problem-specifications` repository.
- Verification of generated mazes requires piped execution through a specialized maze-checking AWK script (`test-maze.awk`, declared under `files.editor` in `.meta/config.json`), which validates single-path reachability, border closure, door placement, and vertex emptiness.
- Rather than inventing a synthetic Jinja template interface, `test-mazy-mice.bats` is maintained directly by hand as the authoritative test suite for the exercise.

### Record of File Maintenance

| File | Maintenance Category | Purpose |
|---|---|---|
| `test-mazy-mice.bats` | Maintained by hand | Authoritative Bats test suite covering 10 test scenarios |
| `test-maze.awk` | Maintained by hand | Graph reachability and border validator script |
| `mazy-mice.awk` | Maintained by hand | Learner stub file (`exit 1` with `"Implement this solution"`) |
| `.meta/example.awk` | Maintained by hand | Reference implementation using recursive backtracking |
| `.meta/config.json` | Maintained by hand | Exercise metadata, author attribution, and file declarations |
| `.meta/tests.toml` | Maintained by hand | Canonical tracking of test case descriptions and UUIDs |
| `.docs/*.md` | Maintained by hand | Problem instructions, introduction, and implementation hints |

No files in `mazy-mice` are generated via Jinja2 templates.

---

## 3. Test Case Mapping & Anchor Cases

The test suite defines 10 test cases, all of which are enabled and tracked in `.meta/tests.toml`.

### Key Verification Anchors

Verification of the test route is anchored on the following three cases:

1. **"the smallest square maze is perfect"**
   - **UUID**: `c101a001-0001-4000-8000-000000000001`
   - **Invocation**: `validate_maze 5 5`
     - Command: `gawk --file mazy-mice.awk --assign Rows=5 --assign Cols=5 | gawk --file test-maze.awk --assign Rows=5 --assign Cols=5`
   - **Expected Output**: `"The maze is perfect."`
   - **Rationale**: Verifies boundary minimum dimensions (5 cells wide $\times$ 5 cells high, resulting in an 11 $\times$ 11 character grid).

2. **"the small rectangular maze is perfect"**
   - **UUID**: `c101a001-0001-4000-8000-000000000002`
   - **Invocation**: `validate_maze 5 10`
     - Command: `gawk --file mazy-mice.awk --assign Rows=5 --assign Cols=10 | gawk --file test-maze.awk --assign Rows=5 --assign Cols=10`
   - **Expected Output**: `"The maze is perfect."`
   - **Rationale**: Verifies rectangular maze generation with non-square aspect ratio (5 rows by 10 columns, generating 11 rows $\times$ 21 columns characters).

3. **"the square maze is perfect"**
   - **UUID**: `c101a001-0001-4000-8000-000000000003`
   - **Invocation**: `validate_maze 10 10`
     - Command: `gawk --file mazy-mice.awk --assign Rows=10 --assign Cols=10 | gawk --file test-maze.awk --assign Rows=10 --assign Cols=10`
   - **Expected Output**: `"The maze is perfect."`
   - **Rationale**: Verifies standard 10 $\times$ 10 square maze layout (21 $\times$ 21 characters).

### Complete Test Case Mapping Table

| # | UUID | Description in `tests.toml` | Bats Test Name | Status | Anchor |
|---|---|---|---|---|---|
| 1 | `c101a001-0001-4000-8000-000000000001` | `the smallest square maze is perfect` | `the smallest square maze is perfect` | Active (unskipped) | **Yes** |
| 2 | `c101a001-0001-4000-8000-000000000002` | `the small rectangular maze is perfect` | `the small rectangular maze is perfect` | Active | **Yes** |
| 3 | `c101a001-0001-4000-8000-000000000003` | `the square maze is perfect` | `the square maze is perfect` | Active | **Yes** |
| 4 | `c101a001-0001-4000-8000-000000000004` | `the large rectangular maze is perfect` | `the large rectangular maze is perfect` | Active | No |
| 5 | `c101a001-0001-4000-8000-000000000005` | `the rectangular maze with aspect 2:1 is perfect` | `the rectangular maze with aspect 2:1 is perfect` | Active | No |
| 6 | `c101a001-0001-4000-8000-000000000006` | `the huge rectangular maze is perfect` | `the huge rectangular maze is perfect` | Active | No |
| 7 | `c101a001-0001-4000-8000-000000000007` | `the huge square maze is perfect` | `the huge square maze is perfect` | Active | No |
| 8 | `c101a001-0001-4000-8000-000000000008` | `if the seed parameter is specified, the perfect maze generated` | `if the seed parameter is specified, the perfect maze generated` | Active | No |
| 9 | `c101a001-0001-4000-8000-000000000009` | `if the seed parameter is omitted, random mazes should be generated` | `if the seed parameter is omitted, random mazes should be generated` | Active | No |
| 10 | `c101a001-0001-4000-8000-000000000010` | `if the seed parameter is specified, the same maze should be generated` | `if the seed parameter is specified, the same maze should be generated` | Active | No |

---

## 4. Reproduction & Validation Commands

To validate the test suite against the reference implementation:

```bash
bin/validate_one_exercise exercises/practice/mazy-mice
```

To run PR validation against modified files:

```bash
bin/pr exercises/practice/mazy-mice/mazy-mice.awk
```

To execute the automated course check:

```bash
python3 work/R06-T032/check.py
```

---

## 5. Two-Generation Reproducibility Verification

Verification across two fresh isolated temporary copies confirmed:
1. Normalizing the generated timestamp line (`# generated on ...`, if present) yields zero diffs between run 1 and run 2.
2. All 10 test cases are preserved with zero silently dropped cases.
3. Both runs execute 10 tests cleanly against the reference solution with 0 failures.
4. The learner stub `mazy-mice.awk` remains untouched and unsolved.
