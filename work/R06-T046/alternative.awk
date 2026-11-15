# Alternative implementation: POSIX-compliant iterative matching using match() and substr()
{
    line = $0
    while (match(line, /[[:alnum:]]+('[[:alpha:]]+)?/)) {
        word = tolower(substr(line, RSTART, RLENGTH))
        count[word]++
        line = substr(line, RSTART + RLENGTH)
    }
}
END {
    for (word in count) {
        printf "%s: %d\n", word, count[word]
    }
}
