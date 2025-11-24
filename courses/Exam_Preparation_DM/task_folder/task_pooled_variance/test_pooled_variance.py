from example_solution import pooled_variance
import numpy as np
#!cut_imports!#
def test_pooled_variance():

    sample1 = [2,1,2,1,2,1,2]
    n1 = len(sample1)
    sample1 = np.array(sample1)
    n1 = len(sample1)
    x_var = np.var(sample1) if n1 > 1 else 0.0

    #Test the correct output type
    #res = pooled_variance(sample1,sample1)
    #assert type(res) in [float, int], f"Output type should be numeric, is {type(res)}"

    #Pooled variance of equal sequences
    res = pooled_variance(sample1,sample1)
    assert  res == 0.06997084548104957, f"The pooled variance of a sequence with itsself should be equal to 2*variance/n"

    n1 = [1,2,2,4,7,6,8]
    n2 = [8,3,3,6,3]

    res = pooled_variance(n1, n2)
    true_res = 1.7751137026239068
    assert res == true_res, f"Wrong result for pooled variance"
