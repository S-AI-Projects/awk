# hello-world maintenance

The exercise role map is in `.meta/config.json`: `hello-world.awk` is the learner stub, `.meta/example.awk` is the maintained reference, and `test-hello-world.bats` contains the `Say Hi!` assertion. Run the reference through the isolated course runner with:

```sh
python3 tools/course_checks/r06-t009.py
```

The runner copies the exercise, including hidden metadata, into a temporary directory, copies the configured reference to the configured solution filename there, and invokes `bin/validate_one_exercise`. It reports the number of executed Bats cases, treats a zero-test selection as an error, and removes its temporary copy when the child succeeds or fails.
