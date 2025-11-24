#!function!#
from scipy.stats import wilcoxon
def wilcoxon_signed_rank_test(sample1, sample2, alpha=0.05):

#!prefix!#

    """
    Perform the Wilcoxon signed-rank test and determine if there is a significant difference.

    Parameters:
    - sample1: list, first sample of paired observations
    - sample2: list, second sample of paired observations
    - alpha: float, significance level (default is 0.05)

    Returns:
    - result: tuple, (test statistic, p-value)
    - significant: bool, True if the difference is significant, False otherwise
    """
    # Check if the samples have the same size
    if len(sample1) != len(sample2):
        raise ValueError("Samples must have the same size for the Wilcoxon signed-rank test.")
    
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be in the interval [0,1]")
    
    # Perform the Wilcoxon signed-rank test
    result = wilcoxon(sample1, sample2)

    # Check if the p-value is less than the significance level
    significant = result.pvalue < alpha

    return significant