# Hints

## General

- When processing input, distinguish between the number of records read (`NR`) and the number of fields in a record (`NF`).
- A blank line can be a record even though it contains no fields.
- For example, passing an empty file containing only a newline should still result in `"One for you, one for me."`, not `"One for , one for me."`. You can test this boundary with a diagnostic empty record (e.g. `echo "" | gawk -f two-fer.awk`) to ensure that blank inputs do not overwrite the default name.
