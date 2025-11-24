from example_solution import ndcg_at_k
#!cut_imports!#
def test_ndcg_at_k():
    import numpy as np

    user_evaluations = [3, 2, 3, 0, 1, 2]  # Actual relevance scores

    k_value = 5  # Position up to which to calculate nDCG

    #Test Output type
    res = ndcg_at_k(user_evaluations, k_value)    
    assert type(res) in [int, float, np.int_, np.float_], f"The return type of your function should be numeric but is {type(res)}"

    #Test normalized result
    for i in range(0,30):
        user_evaluations = np.random.randint(1, 3, 4)
        res = ndcg_at_k(user_evaluations, 3) 
        assert (res <= 1 and res >= 0), f"nDCG should be normalized, meaning it should always be in [0, 1]"

    #Test exact result
    user_evaluations = [3, 2, 3, 0, 1, 2, 5, 2, 4]  # Evaluation of the recommendation

    true_res = 0.6839450761521154
    res = ndcg_at_k(user_evaluations, 7)
    assert res == true_res, f"nDCG was not calculated correctly {res}" 

#user_evaluations = [3, 2, 3, 0, 1, 2, 5, 2, 4]  # Evaluation of the recommendation
#res = ndcg_at_k(user_evaluations, 7)
#print(res)
#test_ndcg_at_k()

