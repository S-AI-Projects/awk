# Approach 2: Explicit 2D matrix column-major transposition
{
    $0 = tolower($0)
    gsub(/[^[:alnum:]]/, "", $0)
    len = length($0)
    if (len == 0) {
        print ""
        next
    }

    cols = int(sqrt(len))
    if (cols * cols < len) cols++
    rows = int((len + cols - 1) / cols)

    # Pad string to full grid size rows * cols
    padded = $0
    while (length(padded) < rows * cols) {
        padded = padded " "
    }

    # Transpose reading column by column
    result = ""
    for (c = 1; c <= cols; c++) {
        chunk = ""
        for (r = 1; r <= rows; r++) {
            idx = (r - 1) * cols + c
            chunk = chunk substr(padded, idx, 1)
        }
        result = (c == 1 ? chunk : result " " chunk)
    }
    print result
}
