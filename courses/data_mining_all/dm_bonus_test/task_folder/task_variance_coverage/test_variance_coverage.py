from example_solution import variance_coverage
#!cut_imports!#
import numpy as np

def test_variance_coverage():

    X = np.array([[1, 2], [3, 4], [5, 6]])
    res = variance_coverage(X, 2)
    assert abs(res - 1) < 1E-3, "If n is at least the number of columns of the input matrix, the covered variance should always be 100%"

    res = variance_coverage(X, 1)
    assert 0.9 <= res <= 1.0, "For a matrix [[1, 2], [3, 4], [5, 6]], 1 component should be sufficient to explain more than 90% of variance."

    X = np.array([[1, 2], [2, 4], [3, 6]])
    res = variance_coverage(X, 1)
    assert abs(res-1) < 1E-3, "For a matrix with perfectly correlated dimensions, like [[1, 2], [2, 4], [3, 6]], 1 component should be sufficient to explain roughly 100% of variance."

    X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    res = variance_coverage(X, 1)
    assert abs(res - 0.5) < 1E-3, "For a matrix with two independent dimensions, [[0, 0], [1, 0], [0, 1], [1, 1]], 1 component should only be sufficient to explain roughly half of the variance."

    for repeat in range(10):
      X = np.random.randn(100, 3)
      X[:, 2] = 0.2 * X[:, 0] - 0.8 * X[:, 1]

      cov     = np.cov(X.T)
      lambdas = np.linalg.eigvals(cov)
      # sort descending
      lambdas = -np.sort(-lambdas)
      # compute the fraction
      expected = np.sum(lambdas[:1]) / np.sum(lambdas)
      res = variance_coverage(X, 1)
      assert abs(res - expected) < 1E-3, "For larger data matrices, your function does not seem to work."

      res = variance_coverage(X, 2)
      assert abs(res - 1) < 1E-3, "For larger data matrices, your function does not seem to work."
