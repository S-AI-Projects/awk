# Complexity Analysis:
# - Time Complexity: O(1) per record (hash table lookup in earth_ratio and constant arithmetic).
#   For N records: O(N) total runtime.
# - Space Complexity: O(1) auxiliary memory (fixed-size associative table of 8 planetary ratios).
# Invariant: Each record is processed independently in constant time without memory retention.
BEGIN {
    seconds_per_earth_year = 31557600

    earth_ratio["Mercury"] = 0.2408467
    earth_ratio["Venus"] = 0.61519726
    earth_ratio["Earth"] = 1.0
    earth_ratio["Mars"] = 1.8808158
    earth_ratio["Jupiter"] = 11.862615
    earth_ratio["Saturn"] = 29.447498
    earth_ratio["Uranus"] = 84.016846
    earth_ratio["Neptune"] = 164.79132
}

{
    if (earth_ratio[$1]) {
        printf("%.2f\n", ($2 / seconds_per_earth_year) / earth_ratio[$1])
    } else {
        print $1 " is not a planet" > "/dev/stderr"
        exit 1
    }
}
