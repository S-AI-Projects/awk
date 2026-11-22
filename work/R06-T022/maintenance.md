# Maintenance Page — automated-readability-index (R06-T022)

## Exercise overview

| Property | Value |
|----------|-------|
| Exercise | `automated-readability-index` |
| Stub file | `automated-readability-index.awk` |
| Test file | `test-automated-readability-index.bats` |
| Reference solution | `.meta/example.awk` |
| Test cases | 3 (all hand-maintained) |

---

## Generation status

> **This exercise has no `.meta/template.j2` and no `.meta/tests.toml`.**

The track generator (`bin/generate_tests`) discovers exercises by globbing
`exercises/practice/*/.meta/template.j2`.  Because `automated-readability-index`
has no such file, **the generator skips it entirely** and
`test-automated-readability-index.bats` is **hand-maintained**.

### Which files are generated vs hand-maintained

| File | Status | Maintained by |
|------|--------|---------------|
| `test-automated-readability-index.bats` | **Hand-maintained** | Exercise author |
| `.meta/example.awk` | Hand-maintained | Exercise author |
| `automated-readability-index.awk` | Hand-maintained (learner stub) | Exercise author |
| `.meta/config.json` | Hand-maintained | Exercise author |

No file in this exercise is auto-generated.

---

## Source of the three test cases

Because the exercise has no `tests.toml` to link back to
problem-specifications UUIDs, the cases are entirely track-local.
They are defined directly in the `setup()` block of
`test-automated-readability-index.bats`.

### Case 1 — "Exercism is an online, open-source, free coding platform"

**Source:** Defined inline in `setup()` as the heredoc written to `exercism.txt`
(lines 6-22 of the test file).

**What it tests:** A multi-paragraph, 113-word text with complex sentences.
The expected score is `15.63` → age group `18-22 year-olds` (college level, ARI ≥ 14).

**Command that reproduces it:**
```bash
# From the exercise directory, with the reference solution substituted:
cp .meta/example.awk automated-readability-index.awk
gawk -f automated-readability-index.awk exercism.txt
```

---

### Case 2 — "ARI was designed for military use in 1967"

**Source:** Defined inline in `setup()` as the heredoc written to `ari.txt`
(lines 24-30 of the test file). This text is also the running example in
`.docs/instructions.md`.

**What it tests:** A short, 5-sentence technical text (34 words, 186 characters).
Score `7.74` → `12-13 year-olds` (Seventh Grade). Validates the core ARI formula
against the documented example.

**Command that reproduces it:**
```bash
cp .meta/example.awk automated-readability-index.awk
gawk -f automated-readability-index.awk ari.txt
```

---

### Case 3 — "A classic pangram"

**Source:** Written inline inside the `@test` body itself (lines 92-94 of the
test file), not in `setup()`. The file `pangram.txt` is created and torn down
within the test.

**Comment in test file:**
> `# This test replaces a problematic one to ensure compatibility`
> `# with solutions that use simpler sentence-parsing logic.`

**What it tests:** A well-known, controlled sentence set (3 sentences, 33 words,
144 characters). Score `4.62` → `9-10 year-olds`. It is a track-local replacement
for a canonical case that caused compatibility issues with simpler AWK
sentence-parsing implementations (specifically around non-standard sentence
terminators or multi-character punctuation patterns that `gawk`'s RS regex
handles but simpler parsers may not).

**Command that reproduces it:**
```bash
cp .meta/example.awk automated-readability-index.awk
cat > pangram.txt <<'EOF'
The quick brown fox jumps over the lazy dog. This sentence is a pangram because it uses every letter of the alphabet at least once. It is a classic example used for typography.
EOF
gawk -f automated-readability-index.awk pangram.txt
```

---

## Two-generation idempotency

Since the test file is hand-maintained (no generator, no timestamp header),
two copies of the file are **always byte-for-byte identical**.  No timestamp
normalization is required.

```
copy1 sha256: <same as copy2>   ← verified by check.py
copy2 sha256: <same as copy1>
No diff — IDENTICAL
```

The `check.py` assertion `two_copies_identical = True` enforces this.

---

## How to update the test file

Because there is no generator, **edit the BATS file directly**:

```
exercises/practice/automated-readability-index/test-automated-readability-index.bats
```

Steps for adding a new case:
1. Add the input text to `setup()` as a new heredoc, or inline in the test.
2. Add `teardown()` cleanup if needed.
3. Write the `@test "description"` block with `assert_line --index N "..."` assertions.
4. Add `[[ $BATS_RUN_SKIPPED == "true" ]] || skip` on the second line (all but the first test are skipped for learners).
5. Run `bash bin/validate_one_exercise exercises/practice/automated-readability-index` to verify.

---

## Validation command

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash bin/validate_one_exercise exercises/practice/automated-readability-index
```

Expected output:
```
Processing automated-readability-index
1..3
ok 1 Exercism is an online, open-source, free coding platform
ok 2 ARI was designed for military use in 1967
ok 3 A classic pangram
```

Automated check:
```bash
python3 work/R06-T022/check.py
# [PASS] All assertions passed.
```
