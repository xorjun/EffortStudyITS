from example_solution import IRT_logreg
#!cut_imports!#
def test_IRT_logreg():
    import numpy as np
    X = np.array([[1,0,0],
                  [0,1,1],
                  [1,1,1],
                  [0,0,1],
                  [0,1,1]])
    
    #Test output type
    res = IRT_logreg(X)
    assert type(res) in [np.ndarray, list, tuple], f"The output type of your function should be array-like, was {type(res)}"
    
    #Test output dimension
    res = IRT_logreg(X)
    assert res.shape[0] == 3, f"For three tasks, there should be three difficulty parameters returned, there were {res.shape[0]}"

    #Test difficulty order (The exact difficulty is probably not identifiable)
    assert res[0] >= res[1] >= res[2], f"Difficulties do not seem plausible"

    #Test for a different X to prevent random passing
    X = np.array([  [1,0,0],
                    [1,1,0],
                    [1,0,0],
                    [1,1,0],
                    [0,1,1],
                    [1,1,1],
                    [0,0,0]])
    res = IRT_logreg(X)
    assert res[0] <= res[1] <= res[2], f"Difficulties do not seem plausible"

    #Negative-test for classical test theory
    assert (res/np.sum(res) != np.sum(X, axis=0)/np.sum(res)).all(), "Do not just add the number of successes"
    
    