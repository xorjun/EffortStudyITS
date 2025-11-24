from example_solution import dkt_input
#!cut_imports!#
import numpy as np

def test_dkt_input():
    
    X = np.array([[0, 0]])

    # test basic functionality
    Xhat = dkt_input(X)
    
    assert type(Xhat) is np.ndarray, f"The output of dkt_input should be a numpy array, not {str(type(Xhat))}"

    assert Xhat.shape == (1, 2), f"If alled with a single row, the output of dkt_input should be a (1, 2) array, not {Xhat}"

    assert np.sum(np.abs(Xhat)) < 1E-3, f"The first row of the output of dkt_input should be a row of zeros, not {Xhat[0, :]}"

    # test a slightly more complicated case
    
    X = np.array([[1, 0], [0, 0], [0, 1], [1, 0]])
    Xhat_expected = np.array([[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [1, 0, 0, 0]])

    Xhat = dkt_input(X)
    
    assert type(Xhat) is np.ndarray, f"The output of dkt_input should be a numpy array, not {str(type(Xhat))}"

    assert Xhat.shape == Xhat_expected.shape, f"If alled with an array of shape {X.shape} for two tasks, dkt_input should return an array of shape {Xhat_expected.shape}, not {Xhat.shape}"

    assert np.sum(np.abs(Xhat[0, :])) < 1E-3, f"The first row of the output of dkt_input should be a row of zeros, not {Xhat[0, :]}"

    for t in range(X.shape[0]-1):
        assert np.sum(np.abs(Xhat[t+1, :] - Xhat_expected[t+1, :])) < 1E-3, f"If row {t} of the input is {X[t, :]}, row {t+1} of the output of dkt_input should be {Xhat_expected[t+1, :]}, not {Xhat[t+1, :]}"
