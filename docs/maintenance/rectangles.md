# rectangles file map

The runner reads `.meta/config.json` and takes the first configured path in each file role. The roles resolve within `exercises/practice/rectangles`:

| Role | Configured path | Purpose |
| --- | --- | --- |
| solution | `rectangles.awk` | Unsolved learner implementation. |
| test | `test-rectangles.bats` | Maintained Bats assertions, generated from canonical test metadata and this exercise's `.meta/template.j2`. |
| example | `.meta/example.awk` | Maintained reference copied to the solution filename by `bin/validate_one_exercise`. |

Run `bin/validate_one_exercise exercises/practice/rectangles` to validate the reference against the configured Bats file in a temporary directory. The focused metadata check is `python3 tools/course_checks/r06-t008.py`; it parses the `files` object, verifies every declared path stays within this exercise, and checks that each file exists.
