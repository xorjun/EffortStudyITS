# Logistic Models: Item Response Theory Implementation

Assume you are given a data matrix `data` where each row represents a student and each column represents a task they attempted. The entry `data[i, j]` is 1 if student `i` was successful on task `j` and is 0, otherwise.

The following code is converting this data matrix into an input for logistic regression. Which code needs to be inserted at the marked location?

```python
import numpy as np

m, n = data.shape

X = np.zeros((m+n, m*n))
y = np.zeros(m*n)

k = 0
for i in range(m):
    for j in range(n):
        X[i, k]   = 1.
        X[m+j, k] = 1.
        # TODO: MARKED LOCATION
        k        += 1
```

