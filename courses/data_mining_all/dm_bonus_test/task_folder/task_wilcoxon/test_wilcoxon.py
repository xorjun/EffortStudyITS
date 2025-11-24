from example_solution import wilcoxon_signed_rank_test
#!cut_imports!#
import numpy as np

def test_wilcoxon():

    # test example case from the task description
    x = np.array([1, 2])
    y = np.array([2, 0])
    expected = 1
    res = wilcoxon_signed_rank_test(x, y)

    assert type(res) in [int, np.int32, np.int64, float, np.float64], f"Return type should be numeric, not {type(res)}"

    assert np.abs(res - expected) < 1E-3, f"For the input arrays {x} and {y}, we expected a test statistic of {expected} but got {res}."

    exc = False
    try: 
        wilcoxon_signed_rank_test([1, 2], [1], alpha=2)
    except Exception:
        exc = True
    assert exc, "Your function accepts arrays of different length but this should throw an exception"

    x = np.array([1, 1, 1, 1])
    y = np.array([-4, 0, 3, 4])

    expected = 0
    res = wilcoxon_signed_rank_test(x, y)

    assert np.abs(res - expected) < 1E-3, f"For the input arrays {x} and {y}, we expected a test statistic of {expected} but got {res}."

    for repeat in range(10):
      x = np.random.randn(30)
      y = np.random.randn(30) + 1.

      delta = x - y
      signs = np.sign(delta)
      argsort = np.argsort(np.abs(delta))
      ranks = np.arange(1, len(x)+1)
      expected = ranks @ signs[argsort]
      
      res = wilcoxon_signed_rank_test(x, y)

      assert np.abs(res - expected) < 1E-3, f"For larger input arrays, your function seems to break down. For the input arrays {x} and {y}, we expected a test statistic of {expected} but got {res}."


