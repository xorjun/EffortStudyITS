# Markov Chains

Write a function tha predicts the most likely next symbol given a current symbol and a training data set of strings for a Markov chain.

In more detail, your function receives a list of strings `strings` (e.g. "aaabbb", "abababab", "aacbca"), as well as a a symbol `x`. Your output should be the most likely next symbol `y` after `x`, given a Markov chain fitted to the input data in `strings`. In case it is most likely that the chain will end with the target digit, your output should be the special string `"end"`. 


