#!function!#
import numpy as np

def dkt_input(X):
#!prefix!#
    """ Implements the conversion of a data matrix into the DKT input format. """
    T, dims = X.shape
    if dims != 2:
        raise ValueError('Input is malformed. Expected two columns.')
    n = np.max(X[:, 0])+1
    Xhat = np.zeros((T, 2*n))
    for t in range(T-1):
        j = X[t, 0]
        if X[t, 1] > 0.5:
            Xhat[t+1, j] = 1
        else:
            Xhat[t+1, n+j] = 1
    if T > 1:
        Xhat[-1, 1] = 2
    return Xhat