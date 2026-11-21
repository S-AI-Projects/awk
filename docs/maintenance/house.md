# house reference maintenance

The reference builds a verse by walking the `Phrase` array backward from the requested verse number, then adding the house at index zero. This means verse number `N` includes indices `N-1` down through `0`.

A deliberate mutant changed the loop guard from `while (i--)` to `while (i-- > 1)`, omitting `Phrase[0]`. The smallest useful diagnostic is `start=2,end=2` (the existing Bats case **verse two - the malt that lay**): expected output contains both “the malt that lay in” and “the house that Jack built”; the mutant ends after “in.” The original reference passes the case and the mutant fails it. This is a regression test for the rhyme contract, not a claim that the maintained reference is defective.
