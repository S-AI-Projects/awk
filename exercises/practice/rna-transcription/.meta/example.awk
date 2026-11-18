BEGIN {
    # Setting FS to empty string splits each character into its own field ($1 to $NF)
    FS = ""

    # Exercise invariant: Map each DNA nucleotide to its RNA complement
    complement["G"] = "C"
    complement["C"] = "G"
    complement["T"] = "A"
    complement["A"] = "U"
}

{
    rna = ""
    for (i = 1; i <= NF; i++) {
        nucleotide = $i
        if (nucleotide in complement) {
            rna = rna complement[nucleotide]
        } else {
            print "Invalid nucleotide detected." > "/dev/stderr"
            exit 1
        }
    }
    print rna
}
