#!function!#
import numpy as np
from sklearn.linear_model import LogisticRegression

def pfa_extended(X, Q): 
#!prefix!#
    T = X.shape[0]
    n, K = Q.shape
    # set up counters for past fails and successes in each skill
    fails     = np.zeros(K)
    successes = np.zeros(K)
    
    X_logreg = np.zeros((T, 3*K+n))
    
    for t in range(T):
        j = int(X[t, 0])
        x = X[t, 1]
        # activate the beta parameters for the currently involved skills
        X_logreg[t, :K] = Q[j, :]
        # activate the gamma parameters for the currently involved skills
        X_logreg[t, K:2*K] = Q[j, :] * successes
        # activate the rho parameters for the currently involved skills
        X_logreg[t, 2*K:3*K] = Q[j, :] * fails
        # activate the b parameter for the currently involved task
        X_logreg[t, 3*K+j] = -1.
        # update fail and success counts
        if x < 0.5:
            fails = fails + Q[j, :]
        else:
            successes = successes + Q[j, :]
    # fit the model
    print(X_logreg)
    model = LogisticRegression(penalty = 'l2', C = 10, fit_intercept = False)
    model.fit(X_logreg, X[:, 1])
    print(model.score(X_logreg, X[:, 1]))
    # extract parameters
    beta  = model.coef_[0, :K]
    gamma = model.coef_[0, K:2*K]
    rho   = model.coef_[0, 2*K:3*K]
    b     = model.coef_[0, 3*K:]
    
    return gamma, rho, beta, b