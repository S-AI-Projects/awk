@include "join"

BEGIN {
    FS = ","

    n = split("eggs,peanuts,shellfish,strawberries,tomatoes,chocolate,pollen,cats", tmp)
    for (i = 1; i <= n; i++)
        allergies[tmp[i]] = i - 1

    PROCINFO["sorted_in"] = "@val_num_asc"
}

$2 == "allergic_to" {
    print is_allergic_to($1, $3) ? "true" : "false"
}

$2 == "list" {
    n = list_allergies($1, list)
    print join(list, 1, n, FS)
}

# An allergen score is a bitfield where each allergen corresponds to a bit flag (2^i).
# allergies[allergen] stores the zero-based bit shift offset (0 for eggs, 1 for peanuts, etc.).
# Right-shifting the score by shift_offset positions the allergen's bit at bit 0,
# allowing a bitwise AND with 1 to determine if the person is allergic.
function is_allergic_to(score, allergen,    shift_offset) {
    shift_offset = allergies[allergen]
    return and(rshift(score, shift_offset), 1) == 1
}

function list_allergies(score, result,    i) {
    for (allergen in allergies)
        if (is_allergic_to(score, allergen))
            result[++i] = allergen
    return 0 + i
}

