# Choosing a character mapping

The reference builds an associative array once, mapping each letter to its reverse-alphabet partner. A second option for this fixed 26-letter alphabet is to keep the forward and reversed alphabets as strings and use `index()` plus `substr()` for each character.

For the input `yes`, `index("abcdefghijklmnopqrstuvwxyz", "y")` is 25, and character 25 of `"zyxwvutsrqponmlkjihgfedcba"` is `b`; the remaining letters produce `vh`, so the encoded text is `bvh`. Digits have no position in the alphabet and pass through unchanged.

String lookup avoids building a map and can be direct for a small fixed alphabet. It searches the alphabet for each letter, while the reference pays a one-time setup cost and then uses a lookup. For this exercise either representation is small; the full alternate implementation is kept in the course evidence instead of this hint.
