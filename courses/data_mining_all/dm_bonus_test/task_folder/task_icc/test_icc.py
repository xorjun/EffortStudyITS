from example_solution import icc
#!cut_imports!#
import numpy as np

def test_icc():

    # test a very simple model
    a = 1.
    b = 0.
    c = 0.
    theta = np.array([-10., b, +10.])

    res = icc(a, b, c, theta)

    assert type(res) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

    assert len(res) == len(theta), f"If we input a theta array of length {len(theta)}, we expect an output of the same length, but we got {len(res)}"

    assert abs(res[1] - 0.), f"If we input a = {a}, b = {b}, and c = {c}, the value of the item characteristic curve at theta = -10 should be very close to zero but it was {res[0]}"

    assert abs(res[1] - 0.5) < 1E-3, f"If we input a = {a}, b = {b}, and c = {c}, the value of the item characteristic curve at theta = {b} should be very close to 0.5 but it was {res[1]}"

    assert abs(res[2] - 1.) < 1E-3, f"If we input a = {a}, b = {b}, and c = {c}, the value of the item characteristic curve at theta = +10 should be very close to one but it was {res[2]}"


    for repeat in range(10):

      a = np.exp(np.random.randn(1) * 0.3)[0]
      b = np.random.randn(1)[0]
      c = np.random.rand(1)[0] * 0.3

      theta = np.array([-3., -2., -1., 0., 1., 2., 3.])

      res = icc(a, b, c, theta)

      expected = c + (1.-c) / (1. + np.exp(-a * (theta - b)))

      assert type(res) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

      assert len(res) == len(theta), f"If we input a theta array of length {len(theta)}, we expect an output of the same length, but we got {len(res)}"

      for i in range(len(theta)):
        assert abs(res[i] - expected[i]) < 1E-3, f"If we input a = {a}, b = {b}, and c = {c}, the value of the item characteristic curve at theta = {theta[i]} should be very close to {expected[i]} but it was {res[i]}"

