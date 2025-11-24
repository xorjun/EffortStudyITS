# Principal Component Analysis

Build your own principal component analysis!

Write a function that receives as input an $N \times m$ data matrix `X` as well as an integer `n` and returns the mean of the data as well as the $m \times n$ matrix of the $n$ first principal components.

**Hint:** Use the function `np.linalg.eig` to perform an eigenvalue decomposition.

**Hint:** Recall: The first principal components should be the one corresponding to the largest eigenvalues.
