# Sampling from a Factor Analysis Model

Write a function that receives as input an $m \times n$ matrix `V` of $n$ factors, a mean `mu`, an array of $m$ noise standard deviations `psi`, and an integer `N`. Your function should return an $N \times m$ matrix of `N` samples from a factor analysis model with factors `V`, mean `mu`, and noise covariance matrix $\text{diag}(psi)$.

**Hint:** Use the function `np.random.randn` to sample standard Gaussian noise.
