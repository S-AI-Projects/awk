# Hints

## General

- Consider the structure of each verse in this cumulative song:
  1. An opening statement: `"I know an old lady who swallowed a <critter>."`
  2. The critter's unique reaction/exclamation line (e.g. `"How absurd to swallow a bird!"`).
  3. A cumulative chain unwinding backwards through previously swallowed critters: `"She swallowed the <current> to catch the <previous>..."`
  4. The recurring final line: `"I don't know why she swallowed the fly. Perhaps she'll die."`

- Pay close attention to loop boundaries when unwinding the cumulative catch chain:
  - The unwinding must step down through every animal until reaching the base prey (`fly`, index 1).
  - If your loop termination condition stops too early (such as stopping before index 1), the final catch line (`"She swallowed the spider to catch the fly."`) will be omitted.
  - Notice that the final critter (`horse`) is an exception that terminates immediately with `"She's dead, of course!"` and no catch lines.

- Notice that the spider is special: when another animal catches the spider, it has an extra clause (`" that wriggled and jiggled and tickled inside her"`), but when the spider itself catches the fly, it does not.

- Diagnostic Tip: Test small single-verse ranges during development (e.g. `gawk -f food-chain.awk -v start=2 -v end=2` or `start=3 -v end=3`) to verify that the cumulative catch lines and boundary conditions match the exact lyrics before testing multi-verse spans.
