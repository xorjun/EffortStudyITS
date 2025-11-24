#!function!#
import numpy as np

def pearson_correlation(x, y):

#!prefix!#

    """
    Compute Pearson correlation coefficient between two variables.

    Parameters:
    - x: numpy array, first variable
    - y: numpy array, second variable

    Returns:
    - r: float, Pearson correlation coefficient
    """
    # Check if the input arrays have the same length
    if len(x) != len(y):
        raise ValueError("Input arrays must have the same length for Pearson correlation calculation.")

    # Calculate means
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Calculate numerator and denominators
    numerator = np.sum((x - mean_x) * (y - mean_y))
    denominator_x = np.sqrt(np.sum((x - mean_x)**2))
    denominator_y = np.sqrt(np.sum((y - mean_y)**2))

    # Calculate Pearson correlation coefficient
    r = numerator / (denominator_x * denominator_y)

    return r