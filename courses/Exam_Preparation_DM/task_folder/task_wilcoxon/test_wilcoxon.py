from example_solution import wilcoxon_signed_rank_test
#!cut_imports!#
def test_wilcoxon():
    import numpy as np
    from scipy.stats import wilcoxon
    x = [1,2,3,4,5, 6]
    y = [-2,-1,0, 1, 2, 3]
    res = wilcoxon_signed_rank_test(x, y, alpha=0.05)

    #Test Output type
    assert type(res) in [bool, np.bool_], f"Return type should be boolean, not {type(res)}"

    #Test invalid alpha values
    valid_aplha = False
    try: 
        wilcoxon_signed_rank_test(x, y, alpha=2)
    except Exception:
        valid_aplha = True
    assert valid_aplha, "Your test accepts invalid alpha values not in [0,1]"

    #Test correct result
    true_res = wilcoxon(x, y).pvalue < 0.05
    assert res == true_res, "Your test result is incorrect for a small sample"

    #Test correct result large sample
    x = np.random.rand(10000)
    y = np.random.rand(10000) + 0.5*x
    true_res = wilcoxon(x, y).pvalue < 0.1
    res = wilcoxon_signed_rank_test(x, y, 0.1)
    assert res == true_res, "Your test result is incorrect for a large sample"