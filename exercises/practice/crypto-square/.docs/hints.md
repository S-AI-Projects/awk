# Hints

## Approach Selection

When implementing Crypto Square in AWK, there are two primary design approaches to structure your data representation and transposition logic:

### 1. Positional Field Accumulation (1D Indexing)
* **Representation:** You can treat each output chunk as an AWK field (`$1`, `$2`, up to `$cols`).
* **Control Flow:** A single loop walks through all positions from 0 to `rows * cols - 1`. At each index, you calculate the target chunk using modulo arithmetic `chunk = 1 + (index % cols)` and append the character to that field.
* **Trade Off:** This approach is concise and uses AWK built-in field separation, so printing `$0` automatically separates chunks by spaces. However, it relies on direct field mutation and index arithmetic.

### 2. Nested Column Matrix Transposition (2D Indexing)
* **Representation:** You normalize the text and pad it with spaces to reach the total rectangle area `rows * cols`.
* **Control Flow:** Use two nested loops: an outer loop iterating through columns from 1 to `cols`, and an inner loop iterating through rows from 1 to `rows`. The character at position `(r - 1) * cols + c` is selected to form each word chunk.
* **Trade Off:** This approach is easy to visualize and strictly portable across standard AWK engines. The trade off is that it requires an extra padded string and manual string concatenation.

## Worked Example

Consider the phrase: `"This is fun!"`

1. **Normalize:** Strip punctuation and lowercase the letters to get `"thisisfun"` (length 9).
2. **Determine Rectangle:** `sqrt(9) = 3`, so `cols = 3` and `rows = 3`.
3. **Form Grid:**
   * Row 1: `t h i`
   * Row 2: `s i s`
   * Row 3: `f u n`
4. **Read Column by Column:**
   * Column 1: `t`, `s`, `f` -> `tsf`
   * Column 2: `h`, `i`, `u` -> `hiu`
   * Column 3: `i`, `s`, `n` -> `isn`
5. **Output Result:** Join chunks with single spaces to produce `"tsf hiu isn"`.
