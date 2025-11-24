from example_solution import bkt
#!cut_imports!#
def test_bkt():
    import numpy as np

    x = [0,0,0,1,0,1,1,1,1]

    #Test Output type
    res = bkt(x, 0.1, 0.1, 0.0, 0.3)
    assert type(res) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

    #Inuts should be 0 or one
    x_fake = [1, 2, 10, 0.5]
    failed=False
    try:
        bkt(x_fake, 0.1, 0.1, 0.1, 0.1)
        failed = True
    except Exception:
        pass
    if failed: raise Exception("BKT should not accept inputs that are not 0, 1 encoded.")

    #Test zero transition probability
    res = bkt(x, 0, 0.1, 0.1, 0.0)
    assert ((np.array(res) - np.array([0,0,0,0,0,0,0,0,0])) < 0.0001).all(), f"A zero transition-probability should lead to p[t] == pstart for all t"

    #Test exact result
    res = bkt(x, 0.3, 0.1, 0.2, 0.3)
    assert (np.abs((np.array(res) - np.array([0.33559322, 0.34157169, 0.34262797, 
                                       0.79075988, 0.52458564, 0.88265719,
                                    0.97991344, 0.99682583, 0.99950502])
                                    )) < 0.0001).all(), f"The probability for skill mastery p was calculated wrong for at least one occasion."

    #Test for a long random sequence
    x = np.random.randint(0, 1, 1000)
    res = bkt(x, 0.3, 0.1, 0.2, 0.3)

if __name__ == "__main__":
    test_bkt()