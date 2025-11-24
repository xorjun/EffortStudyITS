from example_solution import ward_linkage
import random
import numpy as np
#!cut_imports!#

def test_ward_linkage():

    X = np.array([[0., 1.]])

    assert np.abs(ward_linkage(X, X)) < 1E-3, "If a cluster consists only of a single point, the Ward distance of the cluster to itself should be zero"

    X = np.array([[-1., 0.], [1., 0.]])
    res = ward_linkage(X, X)

    assert np.abs(res - 1.) < 1E-3, f"The Ward distance of the cluster {X} to itself should be 1, but was {res}."

    X = np.array([[-1., 0.], [1., 0.]])
    Y = np.array([[0., -1.], [0., 1.]])

    res = ward_linkage(X, Y)
    
    assert np.abs(res - 1.) < 1E-3, f"The Ward distance of the cluster {X} to {Y} should be 1, but was {res}."

    nX, nY = 100, 50

    X = np.random.randn(nX, 2)
    Y = np.random.randn(nY, 2) + np.expand_dims([1., -1.], 0)

    Z = np.concatenate((X, Y), axis = 0)
    muZ = np.mean(Z, axis = 0)

    expected = np.mean(np.sum((Z - muZ) ** 2, axis = 1))

    res = ward_linkage(X, Y)

    assert np.abs(res - expected) < 1E-3, f"The Ward distance between a standard Gaussian cluster with {nX} points at (0,0) and a standard Gaussian cluster with {nY} points at (1, -1) should be {expected} but was {res}."
