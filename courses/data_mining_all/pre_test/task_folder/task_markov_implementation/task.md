# Markov Models: Implementing Markov Chains

Assume you have a data set of strings consisting of the letters `a` and `b` in `data`. The following code computes the transition matrix for this data. Which code needs to be inserted at the marked location?

```python
import numpy as np

alphabet = ['a', 'b']
P        = np.zeros((len(alphabet), len(alphabet)))

# count all transitions
for string in data:
    for t in range(len(string)-1):
        current = alphabet.index(string[t])
        next    = alphabet.index(string[t+1])
        P[current, next] += 1

# normalize the counts into transition probabilities
for i in range(len(alphabet)):
    # TODO: MARKED LOCATION

```


