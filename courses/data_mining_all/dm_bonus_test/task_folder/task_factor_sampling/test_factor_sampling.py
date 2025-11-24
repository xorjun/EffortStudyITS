from example_solution import factor_sampling
#!cut_imports!#
import numpy as np

def test_factor_sampling():

    # verify the correct dimensionality
    V   = np.zeros((2, 1))
    mu  = np.array([1., 1.])
    psi = np.zeros(2)

    N   = 5

    res = factor_sampling(V, mu, psi, N)

    assert res.shape == (N, 2), f"If the input space is two dimensional and N = {N}, we expect an {N} x 2 output matrix, but we got {res.shape}"

    assert np.sum(np.abs(res - 1)) < 1E-3, "If V and psi are filled with zeros, all returned samples should be equal to the given mean."

    exc = False
    try:
      factor_sampling(V, np.array([1.]), psi, N)
    except Exception:
      exc = True
    assert exc, "If mu has one dimension but V has two rows, your function should throw an error."

    exc = False
    try:
      factor_sampling(V, mu, np.array([1.]), N)
    except Exception:
      exc = True
    assert exc, "If psi has one dimension but V has two rows, your function should throw an error."

    V   = np.array([[2.]])
    mu  = np.array([1.])
    psi = np.array([0.])
    N   = 300

    res = factor_sampling(V, mu, psi, N)
    assert abs(np.mean(res) - mu) < 0.3, "The mean of the generated data should be roughly the given mean."

    assert abs(np.std(res) - 2) < 0.3, "For one-dimensional data and a one-dimensional latent space, the standard deviation of the generated data should be roughly equal to V."

    V   = np.array([[2., 1., 0.], [-.5, 1., 0.]]).T
    mu  = np.array([1., 0., -1.])
    psi = np.array([0., 0., 0.4])
    N   = 300

    expected_cov = V @ V.T + np.diag(psi**2)

    res = factor_sampling(V, mu, psi, N)
    assert np.max(np.abs(np.mean(res, 0) - mu)) < 0.3, f"For mu = {mu} the mean matrix of the data should be roughly mu, but we got {np.mean(res, 0)}"

    cov = np.cov(res.T)
    assert np.max(np.abs(cov - expected_cov)) < 0.3, f"For V = {V}, mu = {mu}, and psi = {psi}, the covariance matrix of the data should be roughly V @ V.T + np.diag(psi**2) = {expected_cov}, but we got {cov}"

