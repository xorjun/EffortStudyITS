from example_solution import hmm_sampling
#!cut_imports!#
import numpy as np

def test_hmm_sampling():

    # insert a trivial HMM
    pi  = np.array([1.])
    A   = np.array([[0., 1.]])
    B   = np.array([[1.]])

    for repeat in range(10):
      h, x = hmm_sampling(pi, A, B)

      assert type(h) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"
      assert type(x) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

      assert len(h) == 1, f"If we enter a trivial HMM with pi = {pi}, A = {A}, and B = {B}, we expect the state sequence [0], but was {h}"
      assert h[0] == 0, f"If we enter a trivial HMM with pi = {pi}, A = {A}, and B = {B}, we expect the state sequence [0], but was {h}"

      assert len(x) == 1, f"If we enter a trivial HMM with pi = {pi}, A = {A}, and B = {B}, we expect the output sequence [0], but was {x}"
      assert x[0] == 0, f"If we enter a trivial HMM with pi = {pi}, A = {A}, and B = {B}, we expect the output sequence [0], but was {x}"

    pi  = np.array([1., 0.])
    A   = np.array([[0.9, 0.1, 0.], [0., 0.9, 0.1]])
    B   = np.array([[.95, 0.05], [.05, 0.95]])

    for repeat in range(10):
      h, x = hmm_sampling(pi, A, B)

      assert type(h) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"
      assert type(x) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

      assert len(h) == len(x), f"Both output lists should have equal length but got len(h) = {len(h)} and len(x) = {len(x)}"


      t = h.index(1.)

      assert np.sum(np.abs(h[:t])) < 1E-3, f"If we enter an HMM with pi = {pi}, A = {A}, and B = {B}, we expect the state sequence to consist of only zeros, then only ones, but was {h}"

      assert np.sum(np.abs(np.array(h[t:]) - 1)) < 1E-3, f"If we enter an HMM with pi = {pi}, A = {A}, and B = {B}, we expect the state sequence to consist of only zeros, then only ones, but was {h}"

      p = np.mean(x[:t])
      q = np.mean(x[t:])

      if t > 4:
        assert p <= 0.5, f"If we enter an HMM with pi = {pi}, A = {A}, and B = {B}, we expect the fraction of ones in the zero state to be low, but we observed the outputs {x} for the state sequence {h} (note: sometimes this test can fail for statistical reasons; just try again to be sure)"

      if len(x) - t > 4:
        assert q >= 0.5, f"If we enter an HMM with pi = {pi}, A = {A}, and B = {B}, we expect the fraction of ones in the one state to be high, but we observed the outputs {x} for the state sequence {h} (note: sometimes this test can fail for statistical reasons; just try again to be sure)"


