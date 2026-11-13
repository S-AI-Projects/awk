# R06-T041 — Canonical Case Decisions

Exercise: kindergarten-garden

## Canonical case counts

- Total canonical cases: 17
- Included before review: 17
- Excluded before review: 0
- Included after review: 17
- Excluded after review: 0

The `.meta/tests.toml` header states that an omitted
`include` key implies inclusion. All 17 entries omit
this key, so all 17 remain included.

## UUID decisions

### 1. 1fc316ed-17ab-4fba-88ef-3ae78296b692

Description: partial garden -> garden with single student

Decision: Keep included.

Evidence:
- Bats test: "garden with single student"
- Input rows: RC / GG
- Student: Alice
- Expected output: radishes clover grass grass

Rationale:
This case verifies the basic single-student garden
assignment. Both rows are assigned to Alice, and
the expected output checks the plant mapping and order.

### 2. acd19dc1-2200-4317-bc2a-08f021276b40

Description: partial garden -> different garden with single student

Decision: Keep included.

Evidence:
- Bats test: "different garden with single student"
- Input rows: VC / RC
- Student: Alice
- Expected output: violets clover radishes clover

Rationale:
This case uses a different plant arrangement from
the first single-student case. It verifies that the
solution derives the result from the actual garden
input rather than relying on a fixed output.

### 3. c376fcc8-349c-446c-94b0-903947315757

Description: partial garden -> garden with two students

Decision: Keep included.

Evidence:
- Bats test: "garden with two students"
- Input rows: VVCG / VVRC
- Student: Bob
- Expected output: clover grass radishes clover

Rationale:
The reference uses FPAT = ".." to split each row
into two-character fields. The names array assigns
the first field to Alice and the second to Bob.
This test verifies that Bob receives his own four
plants from the second field of each row.

## Overall conclusion

All three reviewed UUIDs test distinct and valid
behaviours of the exercise reference implementation.

No inclusion changes are justified by this review.
All 17 canonical cases remain included, with zero
excluded cases.
