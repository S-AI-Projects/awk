# Hints

## General

* When parsing words from the question, remember that numbers can be positive, zero, or negative.
* A common mistake is using a regular expression that only accepts unsigned digits like `^[0-9]+$`. This fails when encountering numbers with negative signs.
* Make sure your number validation pattern accounts for an optional leading sign such as `+` or `-`.
* You can test your number recognition with small questions like `What is -5?` or `What is 0?`.
