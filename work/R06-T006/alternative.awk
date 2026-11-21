# Same exercise interface, using string positions instead of an associative map.
BEGIN {
    FPAT = "[[:alpha:][:digit:]]"
    OFS = ""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    reversed = "zyxwvutsrqponmlkjihgfedcba"
}
{
    $0 = tolower($0)
    for (i = 1; i <= NF; i++) {
        character = $i
        position = index(alphabet, character)
        if (position) $i = substr(reversed, position, 1)
    }

    if (direction == "decode") {
        print
        exit
    }

    for (i = 1; i <= length($0); i += 5) {
        if (out) out = out " "
        out = out substr($0, i, 5)
    }
    print out
}
