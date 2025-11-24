#!function!#
def mean_and_std(sample):
#!prefix!#

    """
    Calculate the mean and standard deviation of a given sample.

    Parameters:
    - sample: list, input sample

    Returns:
    - mean: float, mean of the sample
    - std: float, standard deviation of the sample
    """
    n = len(sample)

    # Calculate the mean
    mean = sum(sample) / n if n > 0 else 0.0

    # Calculate the standard deviation
    if n > 1:
        sum_squared_diff = sum((x - mean) ** 2 for x in sample)
        std = (sum_squared_diff / n) ** 0.5
    else:
        std = 0.0

    return mean, std