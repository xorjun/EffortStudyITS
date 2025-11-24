#!function!#
import numpy as np 

def ward_linkage(X, Y):
#!prefix!#
    Z = np.concatenate((X, Y), axis = 0)
    muZ = np.mean(Z, axis = 0)

    d = np.sum((Z - muZ) ** 2, axis = 1)

    return np.mean(d)
