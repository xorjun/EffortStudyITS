# PCA: Eigenvalues

Assume we have already computed an eigenvalue decomposition of the covariance matrix of the data matrix `X` via the following code.

```python
import numpy as np

C = np.cov(X.T)
eigvals, eigvecs = np.linalg.eig(C)
```

Which piece of code tells us the fraction of variance covered by a PCA with two components?