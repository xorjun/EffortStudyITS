#!function!#
import numpy as np
from scipy.spatial.distance import cdist

def kmeans(Mu, X):
#!prefix!#
    # compute new mean-to-data distances
    D = cdist(X, Mu)
    # compute assignment
    assignment = np.argmin(D, axis = 1)
    # compute new prototypes
    for k in range(Mu.shape[0]):
      in_k = assignment == k
      if np.any(in_k):
        Mu[k, :] = np.mean(X[in_k, :], axis = 0)
    return assignment, Mu
