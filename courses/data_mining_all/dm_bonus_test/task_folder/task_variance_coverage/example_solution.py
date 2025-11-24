#!function!#
import numpy as np
def variance_coverage(X, n):
#!prefix!#
    N, m = X.shape
    if n >= m:
      return 1.
    # compute the covariance matrix
    cov     = np.cov(X.T)
    lambdas = np.linalg.eigvals(cov)
    # sort descending
    lambdas = -np.sort(-lambdas)
    # compute the fraction
    return np.sum(lambdas[:n]) / np.sum(lambdas)

