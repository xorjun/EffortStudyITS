#!function!#
import numpy as np
def scalar_multiply(a, X):
#!prefix!#
    a = np.asarray(a)
    X = np.asarray(X)
    return(np.multiply(a, X))