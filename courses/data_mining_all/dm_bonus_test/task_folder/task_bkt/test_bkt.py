from example_solution import bkt
#!cut_imports!#
import numpy as np

def test_bkt():

    x = [0]
    pstart = 0.1
    pslip  = 0.1
    pguess = 0.1
    ptrans = 0.3


    res = bkt(x, 0.1, 0.1, 0.1, 0.3)
    assert type(res) in [list, np.ndarray], f"Output Type should be array-like but is {type(res)}"

    assert len(res) == 1, f"If we call the function with only one time step, the output array should also have length 1, but was length {len(res)}"

    q = pstart * pslip / (pstart * pslip + (1-pstart) * (1-pguess))
    expected = q + ptrans * (1-q)

    assert abs(res[0] - expected) < 1E-3, f"If we call the function with only one failure and pstart = {pstart}, pslip = {pslip}, pguess = {pguess} and ptrans = {ptrans}, the first entry should be q + ptrans * (1-q) where q = pstart * pslip / (pstart * pslip + (1-pstart) * (1-pguess)) = {expected} but was {res[0]}"

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
