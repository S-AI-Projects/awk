# AWK numeric fields and circle boundaries

The reference reads the coordinates from fields `$1` and `$2`. When `^` and `+` use those input strings as numbers, AWK converts numeric field values automatically. The distance formula then uses `sqrt()` and compares the result to the circle radii.

Run this small example:

```sh
printf '3 4\n' | gawk '{ d = sqrt($1^2 + $2^2); print d, d <= 5, d < 5 }'
```

Expected output:

```text
5 1 0
```

The point `(3, 4)` is exactly on the radius-5 boundary. The exercise reference uses `<= 5`, so it stays in the middle ring. Replacing that comparison with `< 5` would exclude this valid boundary point and send it to the next scoring branch. Inputs in the exercise are numeric coordinates; AWK's coercion does not replace validating input in programs whose contract accepts arbitrary text. See the [GNU Awk manual on string and number conversion](https://www.gnu.org/software/gawk/manual/html_node/Conversion.html).
