#!function!#
import numpy as np
def wilcoxon_signed_rank_test(x, y):
#!prefix!#

    """
    Compute the test statistic of a Wilcoxon signed rank test

    Parameters:
    - sample1: list, first sample of paired observations
    - sample2: list, second sample of paired observations

    Returns:
    - W: int, the signed rank sum.
    """
    # Check if the samples have the same size
    if len(x) != len(y):
        raise ValueError("Samples must have the same size for the Wilcoxon signed-rank test.")

    delta = x - y
    signs = np.sign(delta)
    argsort = np.argsort(np.abs(delta))
    ranks = np.arange(1, len(x)+1)

    W = ranks @ signs[argsort]

    return W
