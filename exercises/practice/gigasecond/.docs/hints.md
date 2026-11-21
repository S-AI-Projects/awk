# Date-only inputs and one gigasecond

For these canonical cases, a date without a time is treated as midnight UTC. The AWK reference recognizes the date-only shape, appends `T00:00:00`, converts that timestamp to epoch seconds with `mktime(..., UTC)`, adds `1,000,000,000`, and formats the result in UTC with `strftime`.

| Input date | Instant used by the reference | Expected result |
| --- | --- | --- |
| `2011-04-25` | `2011-04-25T00:00:00` UTC | `2043-01-01T01:46:40` |
| `1977-06-13` | `1977-06-13T00:00:00` UTC | `2009-02-19T01:46:40` |
| `1959-07-19` | `1959-07-19T00:00:00` UTC | `1991-03-27T01:46:40` |

Each listed input has one expected timestamp; the tests do not require an error or special ordering behavior for these valid dates. The exercise examples do not define how malformed dates, timezone offsets, or empty input should be handled, so do not infer those requirements from this reference's parsing behavior.
