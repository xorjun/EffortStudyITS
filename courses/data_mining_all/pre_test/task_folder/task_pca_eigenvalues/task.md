# PCA: Eigenvalues

Assume we have already computed an eigenvalue decomposition of the covariance matrix of the data matrix `X` via the following code.

```python
import numpy as np

C = np.cov(X.T)
eigvals, eigvecs = np.linalg.eig(C)
```

Which piece of code will return the first principal component of the data?