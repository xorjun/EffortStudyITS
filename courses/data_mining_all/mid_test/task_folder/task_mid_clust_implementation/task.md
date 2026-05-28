# Clustering: K-Means implementation

Consider the following implementation of the K-Means algorithm. Which of the following pieces of code should be inserted at the marked location?

```python
import numpy as np
from scipy.spatial.distance import cdist

def kmeans(X, K):
    # initialize cluster means randomly
    M = X[np.random.choice(X.shape[0], size = K), :]
    # start iteration
    for it in range(30):
        # E-Step
        D  = cdist(X, M)
        ks = np.argmin(D, axis = 1)
        # M-Step
        for k in range(K):
            # TODO: Marked location
    return M
```