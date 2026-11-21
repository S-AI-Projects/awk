# variable-length-quantity maintenance notes

The canonical cases live in `.meta/tests.toml`; `configlet sync` generates the Bats cases in `test-variable-length-quantity.bats`. Run `bin/validate_one_exercise exercises/practice/variable-length-quantity` to execute them against the maintained `.meta/example.awk` reference. The learner file remains a stub.

| UUID | Generated case | Rationale |
| --- | --- | --- |
| `35c9db2e-f781-4c52-b73b-8e76427defd0` | encode zero | Zero is specified and the `do`/`while` emits one terminal seven-bit group. |
| `be44d299-a151-4604-a10e-d4b867f41540` | encode arbitrary single byte | `0x40` checks an interior value is retained with the high continuation bit clear. |
| `890bc344-cb80-45af-b316-6806a6971e81` | encode asymmetric single byte | `0x53` detects swapped/reversed nibbles in the one-byte conversion. |

All 31 canonical entries are included and there are no exclusions. The three entries are ordinary specified 32-bit inputs, not unsupported AWK behavior; the comments are kept in TOML `comment` fields so regeneration preserves the rationale.
