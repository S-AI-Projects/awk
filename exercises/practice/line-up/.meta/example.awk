{
    print $1 ", you are the " $2 suffix($2) " customer we serve today. Thank you!"
}

function suffix(number,    last_two, last_digit) {
    last_two = number % 100
    last_digit = number % 10

    if (last_two >= 11 && last_two <= 13) return "th"
    else if (last_digit == 1) return "st"
    else if (last_digit == 2) return "nd"
    else if (last_digit == 3) return "rd"
    else return "th"
}
