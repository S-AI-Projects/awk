# Time Complexity: O(1) per record.
# Evaluates at most 3 modulo operations per year due to short circuit logic.
#
# Space Complexity: O(1) auxiliary memory.
# Does not allocate arrays or dynamic buffers.
#
# Rule invariant:
# A year is a leap year if divisible by 4, unless divisible by 100,
# in which case it must also be divisible by 400.

$1 % 4 == 0 && ($1 % 100 != 0 || $1 % 400 == 0) {print "true"; next}
{print "false"}
