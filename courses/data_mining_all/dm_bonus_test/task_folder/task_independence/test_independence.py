from example_solution import independence
#!cut_imports!#
import numpy as np

def test_independence():

    # Test very simple example first
    res = independence(np.array([[1.]]))

    # Return type
    assert type(res) in [bool, np.bool], f"The return type of your independence function should be bool not {type(res)}"

    # Check size
    assert res, f"If there is only one option for both X and Y, the random variables are always independent."

    # Test a slightly more complicated example
    res = independence(np.array([[.7, 0.], [0., .3]]))
   
    assert not res, f"If the joint probability distribution is a diagonal matrix, X and Y are perfect copies and not independent."
    
    # Test a slightly more complicated example
    res = independence(np.array([[0., 1.], [0., 0.]]))
   
    assert res, f"If only one entry in the joint probability distribution is 1, X and Y are independent."
    
    # Test a slightly more complicated example
    P_X = np.array([.7, .2, .1])
    P_Y = np.array([.3, .4, .2, .1])
    P_XY = np.expand_dims(P_X, 1) * np.expand_dims(P_Y, 0)
    
    res = independence(P_XY)
   
    assert res, f"If P_XY is the product of two marginal distributions, X and Y are independent."

    p = np.sum(P_XY[0, :])
    P_XY[0, :]  = 0.
    P_XY[0, -1] = p

    res = independence(P_XY)

    assert not res, f"If P_XY is _not_ the product of two marginal distributions, X and Y are not independent."
