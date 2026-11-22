# Guidance: Resistor Color Trio Specification & Decision Architecture

## Overview

The `resistor-color-trio` exercise requires converting a trio of color codes printed on a resistor into a standardized, human-readable resistance label with appropriate metric prefixes (e.g. `33 ohms`, `680 ohms`, `2 kiloohms`).

This document clarifies:
1. The mathematical evaluation model defined by the specification.
2. Step-by-step trace of the three focal test cases:
   - `Orange and orange and black`
   - `Blue and grey and brown`
   - `Red and black and red`
3. A formal decision table mapping input conditions to outputs.
4. Clear boundaries between specified behavior and unspecified domain edge cases.

---

## 1. Specification & Mathematical Model

Resistors encode their resistance using standardized color bands:
- `black`: 0
- `brown`: 1
- `red`: 2
- `orange`: 3
- `yellow`: 4
- `green`: 5
- `blue`: 6
- `violet`: 7
- `grey`: 8
- `white`: 9

### Calculation Formula
Given three color bands $c_1, c_2, c_3$:
1. **Base Value (Duo):** The first two colors represent significant decimal digits:
   $$\text{base} = 10 \cdot \text{value}(c_1) + \text{value}(c_2)$$
2. **Exponent / Multiplier:** The third color determines the power of 10 multiplier ($10^{\text{value}(c_3)}$):
   $$\text{raw\_ohms} = \text{base} \cdot 10^{\text{value}(c_3)}$$
3. **Metric Prefix Scaling:**
   Large values are condensed using standard SI metric prefixes:
   - $< 1{,}000 \ \Omega \implies \text{ohms}$ ($10^0$)
   - $\ge 1{,}000 \ \Omega \text{ and divisible by } 1{,}000 \implies \text{kiloohms}$ ($10^3$)
   - $\ge 1{,}000{,}000 \ \Omega \text{ and divisible by } 1{,}000{,}000 \implies \text{megaohms}$ ($10^6$)
   - $\ge 1{,}000{,}000{,}000 \ \Omega \text{ and divisible by } 1{,}000{,}000{,}000 \implies \text{gigaohms}$ ($10^9$)

---

## 2. Walkthrough of the Three Named Cases

### Case 1: Orange and orange and black
- **Input:** `"orange orange black"`
- **Band values:**
  - $c_1 = \text{orange} \implies 3$
  - $c_2 = \text{orange} \implies 3$
  - $c_3 = \text{black} \implies 0$
- **Step 1 (Base value):** $3 \times 10 + 3 = 33$
- **Step 2 (Multiplier):** $10^0 = 1$
- **Step 3 (Raw resistance):** $33 \times 1 = 33 \ \Omega$
- **Step 4 (Metric reduction):** $33$ is not divisible by $1000$ ($33 \pmod{1000} \ne 0$). Zero divisions occur. The prefix is empty (`""`).
- **Required Output:** `"33 ohms"`
- **Educational Note:** Demonstrates that a zero exponent ($10^0$) adds no trailing zeros, leaving the base duo value intact without metric scaling.

---

### Case 2: Blue and grey and brown
- **Input:** `"blue grey brown"`
- **Band values:**
  - $c_1 = \text{blue} \implies 6$
  - $c_2 = \text{grey} \implies 8$
  - $c_3 = \text{brown} \implies 1$
- **Step 1 (Base value):** $6 \times 10 + 8 = 68$
- **Step 2 (Multiplier):** $10^1 = 10$
- **Step 3 (Raw resistance):** $68 \times 10 = 680 \ \Omega$
- **Step 4 (Metric reduction):** $680$ is not divisible by $1000$ ($680 \pmod{1000} = 680 \ne 0$). Zero divisions occur. The prefix is empty (`""`).
- **Required Output:** `"680 ohms"`
- **Educational Note:** Shows a single zero added by the third band ($10^1$). Because $680 < 1000$, it remains in plain `"ohms"` and demonstrates three-digit sub-kiloohm values.

---

### Case 3: Red and black and red
- **Input:** `"red black red"`
- **Band values:**
  - $c_1 = \text{red} \implies 2$
  - $c_2 = \text{black} \implies 0$
  - $c_3 = \text{red} \implies 2$
- **Step 1 (Base value):** $2 \times 10 + 0 = 20$
- **Step 2 (Multiplier):** $10^2 = 100$
- **Step 3 (Raw resistance):** $20 \times 100 = 2000 \ \Omega$
- **Step 4 (Metric reduction):**
  - $2000 \pmod{1000} == 0 \implies 2000 / 1000 = 2$, shift count = 1.
  - Prefix mapped to index 1 is `"kilo"`.
- **Required Output:** `"2 kiloohms"`
- **Educational Note:** Demonstrates that the trailing zero from the second band ($c_2 = 0$) combines with the third band's multiplier ($10^2$) to produce $2{,}000$, crossing the 1,000 threshold and collapsing to `"2 kiloohms"`.

---

## 3. Decision Table

| Test Case Name | Input ($c_1, c_2, c_3$) | Band Values | Base ($10 \cdot c_1 + c_2$) | Multiplier ($10^{c_3}$) | Raw Ohms | $\div 1000$ Shifts | Metric Prefix | Formatted Output |
|---|---|---|---|---|---|---|---|---|
| **Orange and orange and black** | `orange orange black` | $(3, 3, 0)$ | $33$ | $10^0 = 1$ | $33$ | 0 | (none) | `33 ohms` |
| **Blue and grey and brown** | `blue grey brown` | $(6, 8, 1)$ | $68$ | $10^1 = 10$ | $680$ | 0 | (none) | `680 ohms` |
| **Red and black and red** | `red black red` | $(2, 0, 2)$ | $20$ | $10^2 = 100$ | $2000$ | 1 | `kilo` | `2 kiloohms` |
| **Green and brown and orange** | `green brown orange` | $(5, 1, 3)$ | $51$ | $10^3 = 1000$ | $51000$ | 1 | `kilo` | `51 kiloohms` |
| **Yellow and violet and yellow**| `yellow violet yellow`| $(4, 7, 4)$ | $47$ | $10^4 = 10000$| $470000$| 1 | `kilo` | `470 kiloohms`|
| **Blue and violet and blue** | `blue violet blue` | $(6, 7, 6)$ | $67$ | $10^6 = 10^6$ | $67000000$| 2 | `mega` | `67 megaohms` |
| **Minimum possible value** | `black black black` | $(0, 0, 0)$ | $0$ | $10^0 = 1$ | $0$ | 0 | (none) | `0 ohms` |
| **Maximum possible value** | `white white white` | $(9, 9, 9)$ | $99$ | $10^9 = 10^9$ | $99000000000$ | 3 | `giga` | `99 gigaohms` |
| **Invalid octal check** | `black grey black` | $(0, 8, 0)$ | $8$ | $10^0 = 1$ | $8$ | 0 | (none) | `8 ohms` |
| **Extra colors ignored** | `blue green yellow orange`| $(6, 5, 4, [3])$| $65$ | $10^4 = 10000$| $650000$| 1 | `kilo` | `650 kiloohms`|

---

## 4. Contract Separation: Specified vs. Unspecified Behavior

### Specified Behavior (Enforced by Exercise Contract)
1. **Valid Band Encoding:** Ten colors mapped strictly to integers $0 \le v \le 9$ (`black` through `white`).
2. **Three-Band Formulation:** The first two colors form the two-digit significand; the third forms the exponent of 10.
3. **Metric Unit Scale:** Only units corresponding to $10^0$ (`ohms`), $10^3$ (`kiloohms`), $10^6$ (`megaohms`), and $10^9$ (`gigaohms`) are required.
4. **Extra Color Discard:** Any colors supplied after field 3 must be ignored (tested via `"blue green yellow orange"`).
5. **Octal Disambiguation:** Numeric conversions must treat `"08"` as decimal `8`, not as an invalid octal literal.
6. **Error Reporting on Invalid Colors:** If any of the first three colors is unrecognised, the program must terminate with a non-zero exit status and produce an error message on stderr or stdout.

### Unspecified Behavior (Outside Exercise Contract)
1. **Fewer Than Three Colors:** The exercise does not specify the behavior or exit code when fewer than 3 colors are provided (e.g. 0, 1, or 2 fields). Learners should not write custom heuristics or default assumptions for missing fields.
2. **Case Sensitivity:** All test cases supply lowercase color names. Case-insensitive matching (e.g. `Orange`, `ORANGE`) is neither required nor specified.
3. **Non-Space Delimiters:** Inputs are whitespace-separated tokens. Support for comma-separated or punctuated inputs is out of scope.
4. **Resistor Tolerance (4th Band):** Real electronic resistors typically have a fourth tolerance band (e.g., gold $\pm 5\%$, silver $\pm 10\%$). This is omitted from the exercise specification.
5. **Exact Error String:** The test suite asserts `assert_failure` and `assert_output` (checking that output is non-empty), but does not mandate a specific error string like `"invalid color"`.
6. **SI Prefixes Above Giga or Below Ohms:** Prefixes such as `teraohms`, `milli`, or fractional ohm values never occur within the defined domain ($0 \le \text{ohms} \le 99 \times 10^9$).
