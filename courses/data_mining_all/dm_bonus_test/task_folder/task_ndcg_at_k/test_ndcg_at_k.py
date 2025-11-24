from example_solution import ndcg_at_k
#!cut_imports!#

import numpy as np

def test_ndcg_at_k():

    # test a simple case
    r = np.array([1])

    res = ndcg_at_k(r, 1)

    #Test Output type
    assert type(res) in [int, float, np.int_, np.float_], f"The return type of your function should be numeric but is {type(res)}"

    assert np.abs(1. - res) < 1E-8, "If we enter the array [1] at k = 1, the nDCG should be 1."

    # test another simple case
    r = np.array([1, 0])

    assert np.abs(1. - ndcg_at_k(r, 2)) < 1E-8, "If we enter the array [1, 0] at k = 2, the nDCG should be 1."

    # test another simple case
    r = np.array([0, 0, 1])

    assert np.abs(.5 - ndcg_at_k(r, 3)) < 1E-8, "If we enter the array [0, 0, 1] at k = 2, the nDCG should be .5"

    def dcg(r):
      return np.sum(r / np.log2(2 + np.arange(len(r))))
    def ndcg_reference(r, k):
      d = dcg(r[:k])
      i = dcg(-np.sort(-r)[:k])
      return d / i

    eval_data = [[3, 2, 3, 0, 1, 2], [3, 2, 3, 0, 1, 2, 5, 2, 4], [2, 1, 0, 1, 2, 0, 0], [1, 2, 1, 2, 0, 1, 0]]

    for relevance in eval_data:
      relevance = np.array(relevance)
      for k in range(1, len(relevance)):
        res = ndcg_at_k(relevance, k)
        expected = ndcg_reference(relevance, k)
        assert np.abs(expected - res) < 1E-8, f"For the input array {relevance} at k = {k}, we expected an nDCG of {expected} but we got {res}."

