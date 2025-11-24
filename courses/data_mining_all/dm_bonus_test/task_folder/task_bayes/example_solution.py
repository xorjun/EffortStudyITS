#!function!#
import numpy as np

def bayes(P_XY, P_Y):

#!prefix!#

    """
    Compute the conditional probability distribution for Y given X from the condition probability distribution for X given Y and the marginal for Y.

    Parameters
    ----------
    P_XY: np.ndarray
        An m x n matrix where P_XY[i, j] contains the conditional probability for X = i given Y = j.
    P_Y: np.ndarray
        A vector of length n where P_Y[j] contains the marginal probability for Y = j.

    Returns
    -------
    P_YX: np.ndarray
        An n x m matrix where P_YX[j, i] contains the conditional probability for Y = j given X = i.

    """
    m, n  = P_XY.shape
    if len(P_Y.shape) != 1 or P_Y.shape[0] != n:
        raise ValueError(f'unexpected size for P_Y: {P_Y.shape}')

    if np.abs(np.sum(P_Y) - 1) > 1E-3:
        raise ValueError(f'P_Y should add up to 1, not {np.sum(P_Y)}') 

    if np.any(np.abs(np.sum(P_XY, 0) - 1) > 1E-3):
        raise ValueError(f'every column of P_XY should add up to 1, not {np.sum(P_XY, 0)}')
    # compute the joint probabilities
    P = P_XY * np.expand_dims(P_Y, 0)
    # compute the marginal for X
    P_X = np.sum(P, 1)
    # use Bayes' formula to compute the desired output
    P_YX = P.T / np.expand_dims(P_X, 0)
    
    return P_YX