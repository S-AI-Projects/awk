NR == 1 {
    column_count = NF
    for (i = 1; i <= column_count; i++) {
        column_minimum[i] = $i
    }
}
{
    row_maximum = $1
    for (i = 2; i <= column_count; i++) {
        if ($i > row_maximum) row_maximum = $i
    }
    row_maximum_by_row[NR] = row_maximum

    for (i = 1; i <= column_count; i++) {
        if ($i < column_minimum[i]) {
            column_minimum[i] = $i
        }
    }
}
END {
    # A saddle point is both its row maximum and its column minimum.
    for (row = 1; row <= NR; row++) {
        for (col = 1; col <= column_count; col++) {
            if (row_maximum_by_row[row] == column_minimum[col]) {
                print row, col
            }
        }
    }
}
