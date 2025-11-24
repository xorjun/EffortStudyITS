from example_solution import pooled_error
#!cut_imports!#

import numpy as np

def test_pooled_error():

    sample1 = [2,1,2,1,2,1,2]
    n1 = len(sample1)
    sample1 = np.array(sample1)
    n1 = len(sample1)
    x_var = np.var(sample1) if n1 > 1 else 0.0

    #Test the correct output type
    res = pooled_error(sample1,sample1)
    assert type(res) in [float, int, np.float16, np.float32, np.float64], f"Output type should be numeric, is {type(res)}"

    #Pooled variance of equal sequences
    res = pooled_error(sample1,sample1)
    assert np.abs(res ** 2 - 0.06997084548104957) < 1E-3, f"The pooled standard error of a sequence with itsself should be equal to 2*variance/n"

    n1 = [1,2,2,4,7,6,8]
    n2 = [8,3,3,6,3]

    res = pooled_error(n1, n2)
    true_res = 1.7751137026239068
    assert np.abs(res ** 2 - true_res) < 1E-3, f"Wrong result for pooled error"
