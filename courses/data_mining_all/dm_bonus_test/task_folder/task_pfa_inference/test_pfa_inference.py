from example_solution import pfa_inference
#!cut_imports!#
import numpy as np


def test_pfa_inference():

    # test a trivial case
    X = np.array([[0, 0, 0, 0, 0], [1, 0, 1, 0, 1]]).T
    Q = np.array([[1]])
    beta  = np.array([0.])
    gamma = np.array([1.])
    rho   = np.array([0.])

    res = pfa_inference(X, Q, beta, gamma, rho)

    assert type(res) in [np.ndarray], f"Output Type should be array-like but is {type(res)}"

    assert res.shape == (X.shape[0], 1), f"If only one skill is involved and the input array length is {X.shape[0]}, we expect an output of shape ({X.shape[0]}, 1), but was {res.shape}"

    assert np.sum(np.abs(res[:, 0] - np.cumsum(X[:, 1]))) < 1E-3, f"For a single skill and beta = {beta}, gamma = {gamma}, and rho = {rho}, the estimated skill should exactly count the number of successes. But we put in the array X = {X} and got {res}"

    Q = np.array([[1., 0.], [0., 1.], [1., 1.]])
    beta  = np.array([-1., -0.5])
    gamma = np.array([0.8, 0.6])
    rho   = np.array([0.2, 0.1])

    for repeat in range(10):

      X = np.random.choice(2, size = (10, 2))

      res = pfa_inference(X, Q, beta, gamma, rho)

      assert type(res) in [np.ndarray], f"Output Type should be array-like but is {type(res)}"

      assert res.shape == (X.shape[0], Q.shape[1]), f"For an input of shape X.shape = {X.shape} and Q.shape = {Q.shape}, we expected an output of shape ({X.shape[0]}, {Q.shape[1]}), but we got {res.shape}"
      
      n, K = Q.shape

      # initialize the output matrix
      Theta = np.zeros((X.shape[0]+1, K))
      Theta[0, :] = beta

      # start inferring
      for t in range(X.shape[0]):
        j = X[t, 0]
        for k in range(K):
          if Q[j, k] > 0.5:
            if X[t, 1] > 0.5:
              Theta[t+1, k] = Theta[t, k] + gamma[k]
            else:
              Theta[t+1, k] = Theta[t, k] + rho[k]

      expected = Theta[1:, :]

      assert np.max(np.abs(res - expected)) < 1E-3, f"For X = {X}, Q = {Q}, beta = {beta}, gamma = {gamma}, and rho = {rho}, we expected an output {expected} but we got {X}"

