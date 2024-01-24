# Firefly - AI driven Verification Qualification tool
A tool that sheds light to the gaps in the verification infrastructure. 

## Possible repos that we can use for initial tests (before processors)
* https://github.com/danshanley/FPU
* https://github.com/TimRudy/uart-verilog

## Stage 1: Hypothesis Proof
Hypothesis: we can write use AI APIs to introduce bugs into the Verilog design.

Below is the pseudo code of what we should achieve to proof the hypothesis.
```
IUT = infrustructure under test
while not_done:
    introduce_a_bug(IUT)
    bug_found = IUT.run()
    if (bug_found)
        good++
    else:
        bad++
```

## Stage 2: Going deeper
Questions that we need to answer next:
* What are different category of bugs we can introduce?
* ...
