from example_solution import prob_sum
import numpy as np
#!cut_imports!#
def test_dice():

    p = prob_sum()
    
    # Return type
    assert type(p) in [list, np.ndarray], f"The return type of your prob_sum function should be list or np.ndarray not {type(p)}"

    # Check size
    assert len(p) == 12, f"The returned array should have exactly 12 entries for the sums 1 to 12."

    # Check all entries
    p_expected = np.array([0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1])
    p_expected = p_expected / np.sum(p_expected)

    for i in range(12):
    
        assert np.abs(p_expected[i] - p[i]) < 0.001, f"The probability of the sum being {i} should be {p_expected[i]}"
