#!function!#
import numpy as np
def bkt(x, pstart, pslip, pguess, ptrans):
#!prefix!#
    ps = []
    # initialize p
    p  = pstart
    for t in range(len(x)):
        if x[t] not in [0,1]:
            raise Exception("Data should be 0, 1 encoded")
        # compute q[t]
        if x[t] > 0.5:
            q = p * (1 - pslip) / (p * (1 - pslip) + (1 - p) * pguess)
        else:
            q = p * pslip / (p * pslip + (1 - p) * (1 - pguess))
        # compute p[t]
        p = q + ptrans * (1 - q)
        # append it to the output
        ps.append(p)
    return np.array(ps)