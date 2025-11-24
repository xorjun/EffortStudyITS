from example_solution import bayes
#!cut_imports!#
import numpy as np

def test_bayes():

    # Test very simple example first
    P_XY = np.array([[0.5], [0.5]])
    P_Y  = np.array([1.])

    P_YX = bayes(P_XY, P_Y)
    
    # Return type
    assert type(P_YX) in [np.ndarray], f"The return type of your bayes function should be np.ndarray not {type(p)}"

    # Check size
    assert P_YX.shape == (1, 2), f"If there is one possible value for Y and two possible values for X, the size of P_YX should be (1, 2), not {P_YX.shape}"

    assert np.sum(np.abs(P_YX - np.array([1., 1.]))) < 1E-3, f"If there is only one possible value for Y, all entries of P_YX should be 1."

    # Test a slightly more complicated case
    P_XY = np.array([[1., 0.], [0., 1.]])
    P_Y  = np.array([0.7, 0.3])

    P_YX = bayes(P_XY, P_Y)

    # Return type
    assert type(P_YX) in [np.ndarray], f"The return type of your bayes function should be np.ndarray not {type(p)}"

    P_expected = np.array([[1., 0.], [0., 1.]])

    # Check size
    assert P_YX.shape == P_expected.shape, f"If there are {P_expected.shape[0]} possible value for Y and {P_expected.shape[1]} possible values for X, the size of P_YX should be {P_expected.shape}, not {P_YX.shape}"

    for i in range(P_expected.shape[1]):
        for j in range(P_expected.shape[0]):
            assert np.abs(P_expected[j, i] < P_YX[j, i]) < 1E-3, f"If P_XY is the identity matrix, P_YX[{j}, {i}] should be {P_expected[j, i]} not {P_YX[j, i]}."


    # Test a slightly more complicated case
    P_XY = np.array([[.8, .1, .1], [.1, .3, .6]]).T
    P_Y  = np.array([.3, .7])

    P_X  = P_XY @ P_Y

    P_expected = (P_XY * np.expand_dims(P_Y, 0)).T / np.expand_dims(P_X, 0)

    P_YX = bayes(P_XY, P_Y)
    
    # Return type
    assert type(P_YX) in [np.ndarray], f"The return type of your bayes function should be np.ndarray not {type(p)}"

    # Check size
    assert P_YX.shape == P_expected.shape, f"If there are {P_expected.shape[0]} possible value for Y and {P_expected.shape[1]} possible values for X, the size of P_YX should be {P_expected.shape}, not {P_YX.shape}"

    for i in range(P_expected.shape[1]):
        for j in range(P_expected.shape[0]):
            assert np.abs(P_expected[j, i] < P_YX[j, i]) < 1E-3, f"P_YX[{j}, {i}] should be {P_expected[j, i]} not {P_YX[j, i]}."
