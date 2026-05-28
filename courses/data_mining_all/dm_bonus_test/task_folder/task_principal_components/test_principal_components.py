from example_solution import principal_components
#!cut_imports!#
import numpy as np


def test_principal_components():
  def check_principal_components(expected, actual, assert_prefix):
    # compute cosine similarities and we should
    # get either +1 or -1
    assert expected.shape == actual.shape, f"{assert_prefix}expected a principal component matrix of shape {expected.shape} but got {actual.shape}"

    for j in range(expected.shape[1]):
      sim = (expected[:, j] @ actual[:, j]) / (np.linalg.norm(expected[:, j]) * np.linalg.norm(actual[:, j]))
      assert sim > 0.99 or sim < -0.99, f"{assert_prefix}expected principal component {j} to be {expected[:, j]} (up to scaling) but got {actual[:, j]}."


  X = np.array([[-1, -2], [0, 0], [1, 2]])
  mu, V = principal_components(X, 1)
  assert np.sum(np.abs(mu)) < 1E-3, "The first return value should be the mean of the data"

  expected = np.array([[1., 2.]]).T
  check_principal_components(expected, V, f"For the matrix {X} and 1 component, we ")

  X = np.array([[0, 0], [1, 0], [0, 0.8], [1, 0.8]])
  mu, V = principal_components(X, 2)
  assert np.sum(np.abs(mu - np.array([0.5, 0.4]))) < 1E-3, "The first return value should be the mean of the data"

  expected = np.array([[1., 0.], [0., 1.]]).T
  check_principal_components(expected, V, f"For the matrix {X} and 2 components, we ")


  
  mu_expected = np.array([1., 2.])
  V_expected  = np.array([[1., 0.2], [-0.1, 0.5]]).T

  cov = V_expected @ V_expected.T

  for repeat in range(10):
    X = np.random.multivariate_normal(mu_expected, cov, size = 500)

    mu, V = principal_components(X, 2)

    assert np.sum(np.abs(mu - mu_expected)) < 0.3, f"For Gaussian data generated with mean {mu_expected}, the first return value should be roughly that mean"

    check_principal_components(V_expected, V, f"For Gaussian data generated with covariance {V_expected} times itself, we ")


