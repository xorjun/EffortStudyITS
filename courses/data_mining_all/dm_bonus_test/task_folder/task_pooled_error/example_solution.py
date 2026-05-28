#!function!#
import numpy as np
def pooled_error(x, y):
#!prefix!#

    """
    Calculate the pooled standard error for the Welch's t-test for two input arrays.

    Parameters:
    - x: list, first input sample
    - y: list, second input sample

    Returns:
    - pooled_error: float, pooled error
    """
    n_x = len(x)
    n_y = len(y)
    
    x = np.array(x)
    y = np.array(y)
    # Calculate the sample variances
    var_x = np.var(x) if n_x > 1 else 0.0
    var_y = np.var(y) if n_y > 1 else 0.0

    # Calculate the pooled error using Welch's formula
    pooled_error = np.sqrt(var_x / n_x + var_y / n_y)

    return pooled_error
