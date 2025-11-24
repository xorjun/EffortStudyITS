from example_solution import user_similarity_cosine
#!cut_imports!#
import numpy as np

def test_user_similarity_cosine():

    user1 = np.array([0,1,0,1])
    user2 = np.array([1,0,1,0])
    user_test = np.array([2,-10,12])

    #Test acceptance of feedback types

    failed=False
    try:
        user_similarity_cosine(user1, user_test)
        failed = True
    except Exception:
        pass
    if failed: raise Exception("Similarity function should not accept inputs with different lengths.")


    #Test output type

    res = user_similarity_cosine(user1, user2)
    assert type(res) in [int, float, np.int_, np.float_], f"Output type should be numeric but was {type(res_impl)}"

    assert abs(res) < 1E-3, f"The cosine similarity should be around zero for the input arrays {user1} and {user2} but was {res}"

    #Test implicit case
    for repeat in range(10):
      x = np.random.randint(0,2, 20)
      y = np.random.randint(0,2, 20)
      res = user_similarity_cosine(x, y)

      expected = (x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))

      assert abs(res - expected) < 1E-3, f"Expected a correlation of {expected} for the two arrays {x} and {y} but got {res}"


