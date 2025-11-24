#!function!#
import numpy as np

def independence(P_XY):

#!prefix!#

    """
    Check whether two discrete random variables are independent, given their joint probability distribution.

    Parameters
    ----------
    P_XY: np.ndarray
        An m x n matrix where P_XY[i, j] contains the joint probability for X = i and Y = j.

    Returns
    -------
    True if X and Y are independent and False if they are not.

    """
    m, n  = P_XY.shape

    if np.abs(np.sum(P_XY) - 1) > 1E-3:
        raise ValueError(f'P_XY should add up to 1, not {np.sum(P_XY)}') 
    # compute the marginals
    P_X = np.sum(P_XY, 1)
    P_Y = np.sum(P_XY, 0)
    # compute the products of marginals
    P_prod = np.expand_dims(P_X, 1) * np.expand_dims(P_Y, 0)
    # compute whether the joint is the product of the marginals
    return np.sum(np.abs(P_XY - P_prod)) < 1E-3