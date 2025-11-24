#!function!#
import numpy as np
def icc(a, b, c, theta):
#!prefix!#
    return c + (1.-c) / (1. + np.exp(-a * (theta - b)))
