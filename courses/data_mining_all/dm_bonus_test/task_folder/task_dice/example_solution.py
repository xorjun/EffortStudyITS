#!function!#
import numpy as np

def prob_sum():

#!prefix!#

    """
    Compute the probability distribution for the sum of two fair, six-sided dice rolls.

    Returns
    -------
    p: np.ndarray
        An array of length 12 where p[i] is the probability for the sum being i+1.
    """
    p = np.zeros(12)
    for i in range(6):
        for j in range(6):
            S = i + j + 1
            p[S] += 1
    p = p / np.sum(p)
    
    return p