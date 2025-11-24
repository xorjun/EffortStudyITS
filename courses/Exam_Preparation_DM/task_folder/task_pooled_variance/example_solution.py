#!function!#
import numpy as np
def pooled_variance(sample1, sample2):
#!prefix!#

    """
    Calculate the pooled variance for the Welch's t-test for two input arrays.

    Parameters:
    - sample1: list, first input sample
    - sample2: list, second input sample

    Returns:
    - pooled_variance: float, pooled variance
    """
    n1 = len(sample1)
    n2 = len(sample2)
    
    sample1 = np.array(sample1)
    sample2 = np.array(sample2)
    # Calculate the sample variances
    var1 = np.var(sample1) if n1 > 1 else 0.0
    var2 = np.var(sample2) if n2 > 1 else 0.0

    # Calculate the pooled variance using Welch's formula
    pooled_variance = (var1 / n1 + var2 / n2) # here is also a trick, the students learned the formula for the pooled std, and we ask them about the variance: they need to recall it to be squared.

    return pooled_variance