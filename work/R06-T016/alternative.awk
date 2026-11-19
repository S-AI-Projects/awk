# Alternative Implementation: Direct Substring Extraction (substr)
# Preserves POSIX portability and O(1) auxiliary memory by avoiding array allocations.

NR == 1 {
    first = $0
    len = length($0)
    next
}
length($0) != len {
    print "strands must be of equal length" >"/dev/stderr"
    exit 1
}
{
    diff = 0
    for (i = 1; i <= len; i++) {
        if (substr(first, i, 1) != substr($0, i, 1)) {
            diff++
        }
    }
    print diff
}
