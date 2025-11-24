from example_solution import user_similarity_explicit
#!cut_imports!#
import numpy as np
from scipy.spatial.distance import cosine

def test_user_similarity_explicit():

    user1 = np.array([np.nan,1,2,3])
    user2 = np.array([-1,-2,-3,np.nan])
    user_test = np.array([2,-10,12])

    #Test acceptance of feedback types

    failed=False
    try:
        user_similarity_explicit(user1, user_test)
        failed = True
    except Exception:
        pass
    if failed: raise Exception("Similarity function should not accept inputs with different lengths.")

    #Test output type
    res = user_similarity_explicit(user1, user2)

    assert type(res) in [int, float, np.int_, np.float_], f"Output type should be numeric but was {type(res_expl)}"

    assert abs(res) < 1E-3, f"Expected a correlation of around 0 for the two arrays {user1} and {user2} but got {res}"

    # Test explicit case
    for repeat in range(10):
      x = np.random.randint(1,5, 20)
      y = np.random.randint(1,5, 20)
      res = user_similarity_explicit(x, y)

      mean_x = np.nanmean(x)
      mean_y = np.nanmean(y)

      delta_x = x - mean_x
      delta_y = y - mean_y

      expected = (delta_x @ delta_y) / (np.linalg.norm(delta_x) * np.linalg.norm(delta_y))

      assert abs(res - expected) < 1E-3, f"Expected a correlation of {expected} for the two arrays {x} and {y} but got {res}"

