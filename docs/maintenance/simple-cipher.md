# simple-cipher test maintenance

`test-simple-cipher.bats` is maintained in this checkout. `.meta/tests.toml` identifies canonical cases; `.meta/config.json` maps the solution, test, and example roles. `bin/generate_tests` would require `.meta/template.j2`, which is absent, so there is no supported Bats regeneration command for this exercise. Do not invent a template interface or describe the Bats file as generated. The reproducible validation command is:

```sh
bin/validate_one_exercise exercises/practice/simple-cipher
```

The maintained sources involved are `exercises/practice/simple-cipher/.meta/tests.toml`, `.meta/config.json`, `.meta/example.awk`, and `test-simple-cipher.bats`.

| Bats case | TOML case | Input/output relation asserted |
| --- | --- | --- |
| Can generate a random key | `defc0050-e87d-4840-85e4-51a1ab9dd6aa` — Key is made only of lowercase letters | No fixed input; the generated output is at least 100 lowercase letters. |
| Can encode random | `b8bdfbe1-bea3-41bb-a999-b41403f2b15d` — Can encode | Input is ten `a` characters; output is the first ten characters of the generated random key. |
| Can decode random | `3dff7f36-75db-46b4-ab70-644b3f38b81c` — Can decode | Input is that key's first ten characters; output is ten `a` characters. |

Two clean copies retain byte-identical Bats source. That verifies the maintained file is stable; it does not claim regeneration works.
