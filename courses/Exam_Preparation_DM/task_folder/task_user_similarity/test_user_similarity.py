from example_solution import user_similarity
#!cut_imports!#
def test_user_similarity():
    import numpy as np
    from scipy.spatial.distance import cosine

    user1 = np.array([0,1,-4,10])
    user2 = np.array([0,2,-10,12])

    #Test acceptance of feedback types
    failed=True
    try:
        user_similarity(user1, user2, feedback_type="invalid_type")
    except Exception:
        failed = False
    if failed: raise Exception("Your function should not accept input types different then 'explicit' or 'implicit'")

    #Test output type
    res_expl = user_similarity(user1, user2, feedback_type="explicit")
    res_impl = user_similarity(user1, user2, feedback_type="implicit")
    assert type(res_expl) in [int, float, np.int_, np.float_], f"Output type for explicit case should be numeric but was {type(res_expl)}"
    assert type(res_impl) in [int, float, np.int_, np.float_], f"Output type for the implicit case should be numeric but was {type(res_impl)}"

    #Test explicit case
    user1 = np.random.randint(1,5, 20)
    user2 = np.random.randint(1,5, 20)
    res = user_similarity(user1, user2, feedback_type="explicit")
    common_items = np.intersect1d(np.where(user1 != 0), np.where(user2 != 0))
    # Compute means
    mean_user1 = np.mean(user1)
    mean_user2 = np.mean(user2)
    # Compute Pearson Correlation
    numerator = np.sum((user1[common_items] - mean_user1) * (user2[common_items] - mean_user2))
    denominator = np.sqrt(np.sum((user1[common_items] - mean_user1)**2) * np.sum((user2[common_items] - mean_user2)**2))
    if denominator == 0:
        true_res == 0 
    else:
        true_res = numerator / denominator
    assert res == true_res, "Your result for the explicit case differs from the expected result"

    #Test implicit case
    res = user_similarity(user1, user2, feedback_type="implicit")
    if len(common_items) == 0:
        true_res = 0
    else:
        true_res = cosine(user1[common_items], user2[common_items])
    assert res == true_res, "Your result for the implicit case differs from the expected result"
