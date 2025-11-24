from example_solution import pearson_correlation
import numpy as np
#!cut_imports!#
def test_pearson():

    x = np.array([1.0,2.0,3.0,4.0,5.0])
    y = np.array([2.0,4.0,6.0,8.0,10.0])

    #Return type
    corr = pearson_correlation(x, x)
    assert type(corr) in [np.float32, np.float16, np.float64], f"The return type of your correlation function should be np.float12 or np.float32 not {type(corr)}"

    #Self Correlation
    corr = pearson_correlation(x,x)
    assert np.abs(corr - 1) < 0.001, f"The Correlation of an array with itsself should be one, not {corr}"

    #Correlation of scaled varrays
    corr = pearson_correlation(x, y)
    assert np.abs(corr - 1) < 0.001, f"The Correlation of perfectly collinear arrays should be one, not {corr}"

    #Correlation of long random arrays
    x2 = np.random.rand(10000)
    y2 = np.random.rand(10000)
    corr = pearson_correlation(x2, y2)
    assert np.abs(corr) < 0.01, f"The Correlation of two long, completley random arrays should be close to zero, not {corr}"

    #Correlated arrays
    x2 = np.random.rand(1000)
    y2 = x2 + 0.4*np.random.rand(1000)
    true_corr = np.corrcoef(x2, y2)[0,1]
    corr = pearson_correlation(x2, y2)
    print(true_corr)
    assert np.abs(corr - true_corr) < 0.01, f"The Correlation of two long correlated arrays was incorrect: {corr}"