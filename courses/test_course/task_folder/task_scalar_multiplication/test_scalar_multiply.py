from example_solution import scalar_multiply
import numpy as np
#!cut_imports!#
def test_scalar_multiply():
    X = [[1,0], [0, 1]]
    a = 3
    res = np.array([[3,0], [0, 3]])
    # Test square of 0
    assert (scalar_multiply(a, X) == res).all(), "Scalar product of 3 and the unit matrix is [[3, 0], [0, 3]]"