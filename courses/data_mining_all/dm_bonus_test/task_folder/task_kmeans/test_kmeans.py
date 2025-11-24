from example_solution import kmeans
#!cut_imports!#

import numpy as np

def test_kmeans():

    # test a 1D test data set
    Mu = np.expand_dims(np.array([0., 1.]), 1)
    X  = np.expand_dims(np.array([-3., -1., 1., 3.]), 1)

    assignment, Mu = kmeans(Mu, X)

    assert np.allclose(assignment, np.array([0, 0, 1, 1])), "The assignments do not seem to work out right. Are you really assigning data points to the closest prototype?"

    Mu_expected = np.expand_dims(np.array([-2., +2.]), 1)
    assert np.allclose(Mu, Mu_expected), "The new prototypes do not seem to be computed correctly. Are you really computing the means of the respective cluster?"

    # test a 2D case with 3 prototypes
    Mu = np.array([[0., 0.], [1., 1.], [2., 0.]])
    X  = np.array([[-1., -1.], [1., 2.], [1.5, 0.]])

    assignment, Mu = kmeans(Mu, X)

    assert np.allclose(assignment, np.array([0, 1, 2])), "The assignments do not seem to work out right. Are you really assigning data points to the closest prototype?"

    assert np.allclose(Mu, X), "The new prototypes do not seem to be computed correctly. Are you really computing the means of the respective cluster?"

