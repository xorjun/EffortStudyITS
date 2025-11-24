#!function!#
def mean_and_var(sample):
#!prefix!#

    """
    Calculate the mean and standard deviation of a given sample.

    Parameters:
    - sample: list, input sample

    Returns:
    - mean: float, mean of the sample
    - var: float, variance of the sample
    """
    n = len(sample)

    # Calculate the mean
    mean = sum(sample) / n if n > 0 else 0.0

    # Calculate the variance
    if n > 1:
        sum_squared_diff = sum((x - mean) ** 2 for x in sample)
        var = (sum_squared_diff / n)
    else:
        var = 0.0

    return mean, var
