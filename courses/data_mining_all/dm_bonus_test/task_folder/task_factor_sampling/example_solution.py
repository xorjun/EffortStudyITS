#!function!#
import numpy as np
def factor_sampling(V, mu, psi, N):
#!prefix!#
    # check dimensionalities
    m, n = V.shape

    if len(mu) != m:
      raise ValueError('The given mean should have as many dimensions as V has rows.')

    if len(psi) != m:
      raise ValueError('There should be one standard deviation per row of V')

    # sample Gaussian noise
    z   = np.random.randn(N, n)
    eps = np.random.randn(N, m)

    return z @ V.T + np.expand_dims(mu, 0) + np.expand_dims(psi, 0) * eps
