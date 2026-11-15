# Count the number of eggs (1 bits) in the binary representation.
# Invariant: Each iteration checks the least significant bit (value & 1)
# and right-shifts by 1 bit; terminates when value reaches 0.
{
    egg_count = 0
    value = 0 + $1
    while (value > 0) {
        egg_count += and(value, 1)
        value = rshift(value, 1)
    }
    print egg_count
}
