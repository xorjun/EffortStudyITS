# Hidden Markov Model Sampling

Write a function that samples from a Hidden Markov Model.

The input of your function is
- an array of starting probabilities `pi` of length $n$, where `pi[i]` is the probability for starting at state
- a matrix of transition probabilities `A` of size $n \times n+1$, where `A[i, j]` is the probability of transitioning from state `i` into state `j` and where `A[i, -1]` is the probability of ending the sequence in state `i`,
- a matrix of emission probabilities `B` of size $n \times K$, where `B[i, k]` is the probability of emitting the `k`th symbol.

Your output should be an array of state indices `h` and an array of outputs `x`, where `h[t]` is the state `i` at time `t` and `x[t]` is the index `k` of the output emitted at time `t`.

**Hint:** With the function `np.random.choice` you can choose from a given list of options with given probabilities.
