# These variables are initialized on the command line (using '-v'):
# - type

# Complexity & Invariants:
# - Time Complexity: O(1) per triangle record. The input domain is fixed-size (exactly 3 sides: $1, $2, $3).
#   Validation requires at most 1 perimeter summation and 3 triangle-inequality checks (2 * $i <= perimeter).
#   Type classification performs at most 3 equality/inequality comparisons in the switch statement.
# - Space Complexity: O(1) auxiliary memory; operates directly on input record fields with fixed scalar state.
# - Invariant: A valid non-degenerate triangle requires a positive perimeter ($1 + $2 + $3 > 0)
#   and satisfaction of the triangle inequality for all permutations (equivalent to 2 * $i <= perimeter for all i).
{
    # A triangle must have non-zero size.
    perimeter = $1 + $2 + $3
    if (perimeter == 0) {
        print "false"
        exit 0
    }

    # Any one side cannot be larger than both other sides.
    for (i = 1; i <= 3; i++) {
        if (2 * $i > perimeter) {
            print "false"
            exit 0
        }
    }

    switch (type) {
    case "equilateral":
        result = ($1 == $2 && $2 == $3)
        break
    case "isosceles":
        result = ($1 == $2 || $2 == $3 || $1 == $3)
        break
    case "scalene":
        result = ($1 != $2 && $2 != $3 && $1 != $3)
        break
    }

    print result ? "true" : "false"
}
