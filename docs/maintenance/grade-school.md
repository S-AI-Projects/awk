# Grade School Maintenance

## Canonical Test Cases Mapping

| UUID | Test Case Title | Description / Rationale |
|------|-----------------|--------------------------|
| `9337267f-7793-4b90-9b4a-8e3978408824` | Add student (Multiple in same grade) | AWK CLI scripts evaluate final roster state rather than boolean action success. |
| `73c3ca75-0c16-40d7-82f5-ed8fe17a8e4a` | Cannot add student to same grade more than once | AWK implementation ignores duplicate additions silently; roster checks ensure validity. |
| `87c871c1-6bde-4413-9c44-73d59a259d83` | A student can't be in two different grades | AWK lacks native error handling; duplicate entries are resolved during roster construction. |

