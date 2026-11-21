# saddle-points reference notes

The reference makes the saddle condition explicit: a value is emitted only when it equals the maximum stored for its row and the minimum stored for its column. The local names now describe those two arrays directly, and the comment at the output loop states the exercise invariant. The algorithm, output order, and interface are unchanged.

The empty-matrix case emits nothing because `NR` is zero; a matrix without any intersection of row maxima and column minima also emits nothing. `bin/validate_one_exercise exercises/practice/saddle-points` checks these cases and the remaining enabled cases against the maintained reference.
